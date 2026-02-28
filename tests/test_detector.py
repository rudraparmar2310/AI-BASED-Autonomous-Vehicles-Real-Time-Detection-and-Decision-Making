"""
Tests for the WIoU loss and YOLOv8 detector.
"""

import sys
import types
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import torch


# ---------------------------------------------------------------------------
# WIoU Loss tests
# ---------------------------------------------------------------------------

class TestWIoULoss(unittest.TestCase):
    """Unit tests for WIoULoss."""

    def setUp(self):
        from detection.wiou_loss import WIoULoss
        self.WIoULoss = WIoULoss

    def _make_boxes(self, n=4):
        """Create random (cx, cy, w, h) boxes in [0,1]."""
        torch.manual_seed(42)
        boxes = torch.rand(n, 4)
        boxes[:, 2:] = boxes[:, 2:].abs() + 0.05  # ensure positive w/h
        return boxes

    def test_loss_is_scalar(self):
        loss_fn = self.WIoULoss()
        pred = self._make_boxes()
        target = self._make_boxes()
        loss = loss_fn(pred, target)
        self.assertEqual(loss.shape, torch.Size([]))

    def test_zero_loss_for_perfect_prediction(self):
        """When pred == target, loss should be near 0."""
        loss_fn = self.WIoULoss(monotonic_focal=False)
        boxes = self._make_boxes()
        loss = loss_fn(boxes, boxes.clone())
        self.assertAlmostEqual(loss.item(), 0.0, places=4)

    def test_loss_non_negative(self):
        loss_fn = self.WIoULoss()
        pred = self._make_boxes(8)
        target = self._make_boxes(8)
        loss = loss_fn(pred, target)
        self.assertGreaterEqual(loss.item(), 0.0)

    def test_focal_vs_no_focal(self):
        """Focal variant should weight samples differently than non-focal."""
        # Use boxes with deliberately mixed quality (some good, some bad)
        # so the focusing coefficient produces meaningfully different weighting.
        pred = torch.tensor([
            [0.5, 0.5, 0.4, 0.4],   # near-perfect
            [0.5, 0.5, 0.4, 0.4],   # near-perfect
            [0.5, 0.5, 0.4, 0.4],   # near-perfect
            [0.9, 0.9, 0.3, 0.3],   # badly misaligned
            [0.1, 0.1, 0.3, 0.3],   # badly misaligned
        ])
        target = torch.tensor([
            [0.5, 0.5, 0.4, 0.4],
            [0.5, 0.5, 0.4, 0.4],
            [0.5, 0.5, 0.4, 0.4],
            [0.5, 0.5, 0.3, 0.3],
            [0.5, 0.5, 0.3, 0.3],
        ])

        focal = self.WIoULoss(monotonic_focal=True)(pred, target)
        no_focal = self.WIoULoss(monotonic_focal=False)(pred, target)
        # Focal weighting emphasises hard samples differently → distinct values
        self.assertNotAlmostEqual(focal.item(), no_focal.item(), places=3)

    def test_gradient_flows(self):
        """Loss should be differentiable w.r.t. pred."""
        loss_fn = self.WIoULoss()
        pred = self._make_boxes().requires_grad_(True)
        target = self._make_boxes()
        loss = loss_fn(pred, target)
        loss.backward()
        self.assertIsNotNone(pred.grad)
        self.assertFalse(torch.isnan(pred.grad).any())


# ---------------------------------------------------------------------------
# YOLOv8 Detector tests (model mocked)
# ---------------------------------------------------------------------------

class TestDetectionResult(unittest.TestCase):
    """Tests for the DetectionResult dataclass."""

    def setUp(self):
        from detection.detector import DetectionResult
        self.DetectionResult = DetectionResult

    def test_center_property(self):
        det = self.DetectionResult(
            class_id=0, class_name="car", confidence=0.9, bbox=(100, 50, 300, 200)
        )
        self.assertEqual(det.center, (200.0, 125.0))

    def test_area_property(self):
        det = self.DetectionResult(
            class_id=0, class_name="car", confidence=0.9, bbox=(0, 0, 100, 50)
        )
        self.assertAlmostEqual(det.area, 5000.0)

    def test_distance_estimate_default_none(self):
        det = self.DetectionResult(
            class_id=0, class_name="car", confidence=0.9, bbox=(0, 0, 100, 50)
        )
        self.assertIsNone(det.distance_estimate)


class TestYOLOv8Detector(unittest.TestCase):
    """Tests for YOLOv8Detector with a mocked ultralytics YOLO."""

    def _make_mock_yolo(self, detections):
        """Build a mock YOLO result containing *detections*."""
        # Each detection is (class_id, class_name, conf, x1, y1, x2, y2)
        mock_box_list = []
        names = {}
        for cls_id, cls_name, conf, x1, y1, x2, y2 in detections:
            names[cls_id] = cls_name
            box = MagicMock()
            box.cls = [cls_id]
            box.conf = [conf]
            box.xyxy = [torch.tensor([x1, y1, x2, y2], dtype=torch.float32)]
            mock_box_list.append(box)

        mock_result = MagicMock()
        mock_result.names = names
        mock_result.boxes = mock_box_list

        mock_yolo = MagicMock()
        mock_yolo.predict.return_value = [mock_result]
        mock_yolo.names = names
        return mock_yolo

    def test_detect_returns_list_of_detection_results(self):
        from detection.detector import DetectionResult, YOLOv8Detector

        detector = YOLOv8Detector(model_path="yolov8n.pt", conf_threshold=0.3)
        mock_yolo = self._make_mock_yolo(
            [(0, "car", 0.85, 100, 50, 300, 200), (1, "person", 0.72, 400, 100, 480, 300)]
        )
        detector._model = mock_yolo

        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        results = detector.detect(frame)

        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], DetectionResult)
        self.assertEqual(results[0].class_name, "car")
        self.assertAlmostEqual(results[0].confidence, 0.85, places=4)

    def test_detect_empty_frame(self):
        from detection.detector import YOLOv8Detector

        detector = YOLOv8Detector()
        mock_yolo = self._make_mock_yolo([])
        detector._model = mock_yolo

        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        results = detector.detect(frame)
        self.assertEqual(results, [])

    def test_distance_estimate_with_focal_length(self):
        from detection.detector import YOLOv8Detector

        detector = YOLOv8Detector(focal_length_px=800.0)
        mock_yolo = self._make_mock_yolo(
            [(0, "car", 0.90, 100, 100, 300, 250)]
        )
        detector._model = mock_yolo

        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        results = detector.detect(frame)
        # car height = 250 - 100 = 150 px, real height = 1.5 m, f = 800
        expected = round(1.5 * 800 / 150, 2)
        self.assertAlmostEqual(results[0].distance_estimate, expected, places=2)

    def test_no_distance_without_focal_length(self):
        from detection.detector import YOLOv8Detector

        detector = YOLOv8Detector(focal_length_px=None)
        mock_yolo = self._make_mock_yolo([(0, "car", 0.90, 100, 100, 300, 250)])
        detector._model = mock_yolo

        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        results = detector.detect(frame)
        self.assertIsNone(results[0].distance_estimate)


if __name__ == "__main__":
    unittest.main()
