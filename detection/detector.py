"""
YOLOv8-based real-time object detector with WIoU-optimised training.

This module wraps the Ultralytics YOLOv8 model and provides:
- A clean ``detect`` API that returns structured ``DetectionResult`` objects.
- A ``train_with_wiou`` helper that fine-tunes / trains a model using the
  custom WIoULoss instead of the default CIoU regression head.

Typical usage::

    detector = YOLOv8Detector(model_path="yolov8n.pt", conf_threshold=0.4)
    results = detector.detect(frame)            # frame: np.ndarray (H, W, 3)
    for det in results:
        print(det.class_name, det.confidence, det.bbox)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy import of heavy dependencies so that unit-tests can mock them easily.
# ---------------------------------------------------------------------------

def _import_ultralytics():
    try:
        from ultralytics import YOLO  # noqa: PLC0415
        return YOLO
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "ultralytics is required for YOLOv8Detector. "
            "Install it with: pip install ultralytics"
        ) from exc


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class DetectionResult:
    """A single object detection result.

    Attributes:
        class_id (int): Numeric class index.
        class_name (str): Human-readable class label.
        confidence (float): Detection confidence in [0, 1].
        bbox (tuple[float, float, float, float]): Bounding box in
            ``(x1, y1, x2, y2)`` pixel coordinates.
        distance_estimate (float | None): Approximate distance in metres,
            computed from the projected bounding-box height when camera
            intrinsics are provided.
    """

    class_id: int
    class_name: str
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2)
    distance_estimate: Optional[float] = field(default=None)

    @property
    def center(self) -> tuple:
        """Return the (cx, cy) centre of the bounding box."""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    @property
    def area(self) -> float:
        """Return the bounding-box pixel area."""
        x1, y1, x2, y2 = self.bbox
        return max(0.0, x2 - x1) * max(0.0, y2 - y1)


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------

# Approximate real-world object heights (metres) used for monocular distance
# estimation via the pinhole camera model:  d = (h_real * f) / h_pixels
_REAL_HEIGHT_M: dict[str, float] = {
    "person": 1.75,
    "car": 1.50,
    "truck": 3.50,
    "bus": 3.20,
    "motorcycle": 1.20,
    "bicycle": 1.10,
    "traffic light": 0.80,
    "stop sign": 0.75,
    "fire hydrant": 0.60,
}


class YOLOv8Detector:
    """Real-time object detector backed by YOLOv8.

    Args:
        model_path (str | Path): Path to a ``.pt`` weights file or a
            YOLOv8 model name (e.g. ``"yolov8n.pt"``).
        conf_threshold (float): Minimum confidence to keep a detection.
        iou_threshold (float): NMS IoU threshold.
        device (str): PyTorch device string (``"cpu"``, ``"cuda"``, …).
        focal_length_px (float | None): Camera focal length in pixels.  When
            provided, monocular distance estimates are attached to each result.
        classes (list[int] | None): Restrict detection to these class IDs.
    """

    def __init__(
        self,
        model_path: Union[str, Path] = "yolov8n.pt",
        conf_threshold: float = 0.4,
        iou_threshold: float = 0.45,
        device: str = "cpu",
        focal_length_px: Optional[float] = None,
        classes: Optional[List[int]] = None,
    ) -> None:
        self.model_path = str(model_path)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        self.focal_length_px = focal_length_px
        self.classes = classes
        self._model = None  # Lazy load

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_model(self):
        if self._model is None:
            YOLO = _import_ultralytics()
            self._model = YOLO(self.model_path)
            logger.info("Loaded YOLOv8 model from %s", self.model_path)
        return self._model

    def _estimate_distance(self, class_name: str, bbox: tuple) -> Optional[float]:
        """Monocular distance estimate using known object height."""
        if self.focal_length_px is None:
            return None
        h_real = _REAL_HEIGHT_M.get(class_name.lower())
        if h_real is None:
            return None
        _, y1, _, y2 = bbox
        h_pixels = y2 - y1
        if h_pixels <= 0:
            return None
        return round((h_real * self.focal_length_px) / h_pixels, 2)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect(self, frame: np.ndarray) -> List[DetectionResult]:
        """Run inference on a single BGR/RGB frame.

        Args:
            frame (np.ndarray): Image array with shape ``(H, W, 3)``.

        Returns:
            list[DetectionResult]: All detections above *conf_threshold*.
        """
        model = self._load_model()
        results = model.predict(
            source=frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            device=self.device,
            classes=self.classes,
            verbose=False,
        )

        detections: List[DetectionResult] = []
        for r in results:
            names = r.names
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = names.get(cls_id, str(cls_id))
                conf = float(box.conf[0])
                x1, y1, x2, y2 = (float(v) for v in box.xyxy[0])
                bbox = (x1, y1, x2, y2)
                dist = self._estimate_distance(cls_name, bbox)
                detections.append(
                    DetectionResult(
                        class_id=cls_id,
                        class_name=cls_name,
                        confidence=conf,
                        bbox=bbox,
                        distance_estimate=dist,
                    )
                )

        logger.debug("Detected %d objects", len(detections))
        return detections

    def train_with_wiou(
        self,
        data_yaml: str,
        epochs: int = 50,
        imgsz: int = 640,
        batch: int = 16,
        project: str = "runs/train",
        name: str = "wiou_yolov8",
    ) -> None:
        """Fine-tune the model using WIoU loss.

        This method patches the bounding-box regression loss of the YOLOv8
        training loop with :class:`~detection.wiou_loss.WIoULoss` and then
        calls the standard Ultralytics trainer.

        Args:
            data_yaml (str): Path to the dataset YAML file.
            epochs (int): Number of training epochs.
            imgsz (int): Training image size.
            batch (int): Batch size.
            project (str): Output project directory.
            name (str): Experiment name.
        """
        import torch  # noqa: PLC0415
        from .wiou_loss import WIoULoss  # noqa: PLC0415

        model = self._load_model()
        wiou = WIoULoss(scale=1.0, monotonic_focal=True)

        # Patch the loss at the model level so the trainer uses WIoU.
        # Ultralytics exposes the loss criterion via model.model.criterion.
        original_box_loss = None
        if hasattr(model.model, "criterion") and hasattr(model.model.criterion, "box"):
            original_box_loss = model.model.criterion.box

            def _wiou_wrapper(pred_bboxes, target_bboxes, *args, **kwargs):  # noqa: ARG001
                return wiou(pred_bboxes, target_bboxes)

            model.model.criterion.box = _wiou_wrapper
            logger.info("Replaced YOLOv8 box loss with WIoULoss.")

        try:
            model.train(
                data=data_yaml,
                epochs=epochs,
                imgsz=imgsz,
                batch=batch,
                project=project,
                name=name,
                exist_ok=True,
            )
        finally:
            # Restore original loss to avoid side effects if model is reused.
            if original_box_loss is not None:
                model.model.criterion.box = original_box_loss
