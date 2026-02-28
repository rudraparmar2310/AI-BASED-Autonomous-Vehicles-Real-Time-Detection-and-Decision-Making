"""
Visualization utilities for the autonomous driving perception system.

Provides :class:`Visualizer` which overlays:
- Bounding boxes coloured by risk level (green / amber / red).
- Class label, confidence, and estimated distance.
- The current driving command (STOP / SLOW / GO) as a HUD overlay.
- An optional risk-score bar chart for debugging.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

# OpenCV is imported lazily so the module remains importable in test
# environments where it might not be installed.
def _cv2():
    try:
        import cv2  # noqa: PLC0415
        return cv2
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "opencv-python is required for Visualizer. "
            "Install it with: pip install opencv-python"
        ) from exc


# Colour palette (BGR) for risk levels
_COLOURS = {
    "low": (0, 200, 0),       # green
    "medium": (0, 165, 255),  # orange
    "high": (0, 0, 220),      # red
}

# Command banner colours (BGR)
_CMD_COLOURS = {
    "GO": (0, 180, 0),
    "SLOW": (0, 140, 255),
    "STOP": (0, 0, 220),
}


class Visualizer:
    """Overlay detections and the driving command on a video frame.

    Args:
        slow_threshold (float): Risk score above which a box is coloured amber.
        stop_threshold (float): Risk score above which a box is coloured red.
        font_scale (float): OpenCV font scale for labels.
        box_thickness (int): Bounding-box line thickness.
    """

    def __init__(
        self,
        slow_threshold: float = 0.30,
        stop_threshold: float = 0.65,
        font_scale: float = 0.55,
        box_thickness: int = 2,
    ) -> None:
        self.slow_threshold = slow_threshold
        self.stop_threshold = stop_threshold
        self.font_scale = font_scale
        self.box_thickness = box_thickness

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _risk_colour(self, score: float) -> tuple:
        if score >= self.stop_threshold:
            return _COLOURS["high"]
        if score >= self.slow_threshold:
            return _COLOURS["medium"]
        return _COLOURS["low"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def draw(
        self,
        frame: np.ndarray,
        risk_scores,
        command: Optional[str] = None,
    ) -> np.ndarray:
        """Draw detections and the driving command on *frame*.

        Args:
            frame (np.ndarray): BGR image array (modified in-place copy).
            risk_scores (list[RiskScore]): Scored detections to overlay.
            command (str | None): Driving command string (``"GO"``, ``"SLOW"``,
                ``"STOP"``).

        Returns:
            np.ndarray: Annotated BGR image (same resolution as input).
        """
        cv2 = _cv2()
        out = frame.copy()

        for rs in risk_scores:
            det = rs.detection
            x1, y1, x2, y2 = (int(v) for v in det.bbox)
            colour = self._risk_colour(rs.score)

            # Bounding box
            cv2.rectangle(out, (x1, y1), (x2, y2), colour, self.box_thickness)

            # Label: class + confidence + distance
            label_parts = [
                f"{det.class_name} {det.confidence:.2f}",
                f"risk={rs.score:.2f}",
            ]
            if det.distance_estimate is not None:
                label_parts.append(f"d={det.distance_estimate}m")
            label = "  ".join(label_parts)

            (tw, th), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, 1
            )
            ty = max(y1 - baseline - 4, th + 4)
            cv2.rectangle(
                out,
                (x1, ty - th - baseline),
                (x1 + tw + 4, ty + baseline),
                colour,
                -1,
            )
            cv2.putText(
                out,
                label,
                (x1 + 2, ty),
                cv2.FONT_HERSHEY_SIMPLEX,
                self.font_scale,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

        # Command banner
        if command is not None:
            banner_colour = _CMD_COLOURS.get(command, (128, 128, 128))
            h, w = out.shape[:2]
            banner_h = 50
            cv2.rectangle(out, (0, 0), (w, banner_h), banner_colour, -1)
            cv2.putText(
                out,
                f"Command: {command}",
                (20, 35),
                cv2.FONT_HERSHEY_DUPLEX,
                1.2,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        return out
