"""
Adaptive risk scoring module.

Each detected object is assigned a *risk score* in ``[0, 1]`` based on:

1. **Object class criticality** – pedestrians and cyclists score higher than
   static infrastructure objects.
2. **Proximity** – closer objects exponentially increase the risk score.
3. **Confidence** – detections with lower confidence reduce the risk contribution.
4. **Relative position** – objects in the ego-vehicle lane (horizontally centred
   in the image) are weighted more heavily than peripheral detections.

The scores are *adaptive*: the proximity weight decays with the inverse of
distance, so very distant objects have a negligible contribution while objects
within the critical zone dominate.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional

from detection.detector import DetectionResult


# ---------------------------------------------------------------------------
# Per-class criticality weights (higher ⟹ more dangerous)
# ---------------------------------------------------------------------------

_CLASS_CRITICALITY: dict[str, float] = {
    # Vulnerable road users
    "person": 1.0,
    "bicycle": 0.9,
    "motorcycle": 0.85,
    # Vehicles
    "car": 0.75,
    "truck": 0.80,
    "bus": 0.80,
    "train": 0.90,
    # Infrastructure & signage
    "traffic light": 0.60,
    "stop sign": 0.70,
    "fire hydrant": 0.40,
    # Animals
    "dog": 0.65,
    "cat": 0.50,
    "horse": 0.80,
    # Default for unknown classes
    "__default__": 0.50,
}

# Distance thresholds (metres)
_CRITICAL_DIST_M: float = 10.0   # Below this → maximum proximity weight
_SAFE_DIST_M: float = 50.0       # Above this → proximity weight approaches 0


@dataclass
class RiskScore:
    """Risk assessment for a single detected object.

    Attributes:
        detection (DetectionResult): The underlying detection.
        class_criticality (float): Weight derived from the object class.
        proximity_weight (float): Weight based on estimated distance.
        lane_weight (float): Weight based on lateral position in the image.
        score (float): Final aggregated risk score in ``[0, 1]``.
    """

    detection: DetectionResult
    class_criticality: float
    proximity_weight: float
    lane_weight: float
    score: float


class RiskScorer:
    """Compute an adaptive risk score for a list of detections.

    Args:
        image_width (int): Width of the source image in pixels; used to
            determine the lane centre for lateral weighting.
        critical_distance_m (float): Distance below which the proximity weight
            is 1.0 (maximum danger).
        safe_distance_m (float): Distance above which the proximity weight is
            effectively zero.
        lane_width_fraction (float): Fraction of image width considered the
            ego lane (centred).  Objects outside this zone receive a reduced
            lateral weight.
    """

    def __init__(
        self,
        image_width: int = 1280,
        critical_distance_m: float = _CRITICAL_DIST_M,
        safe_distance_m: float = _SAFE_DIST_M,
        lane_width_fraction: float = 0.33,
    ) -> None:
        self.image_width = image_width
        self.critical_distance_m = critical_distance_m
        self.safe_distance_m = safe_distance_m
        self.lane_width_fraction = lane_width_fraction

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _class_criticality(self, class_name: str) -> float:
        return _CLASS_CRITICALITY.get(
            class_name.lower(), _CLASS_CRITICALITY["__default__"]
        )

    def _proximity_weight(self, distance_m: Optional[float]) -> float:
        """Sigmoid-like decay: 1.0 at ``critical_distance_m``, →0 at ``safe_distance_m``."""
        if distance_m is None:
            # No distance info → use a conservative mid-range weight
            return 0.5
        if distance_m <= self.critical_distance_m:
            return 1.0
        if distance_m >= self.safe_distance_m:
            return 0.0
        # Smooth cosine interpolation in (critical, safe)
        ratio = (distance_m - self.critical_distance_m) / (
            self.safe_distance_m - self.critical_distance_m
        )
        return round(0.5 * (1.0 + math.cos(math.pi * ratio)), 4)

    def _lane_weight(self, bbox: tuple) -> float:
        """Weight based on the horizontal position of the detection centre."""
        cx = (bbox[0] + bbox[2]) / 2
        half_lane = self.image_width * self.lane_width_fraction / 2
        img_centre = self.image_width / 2
        lateral_dist = abs(cx - img_centre)
        if lateral_dist <= half_lane:
            return 1.0
        # Linear fall-off outside the lane zone
        max_lateral = self.image_width / 2
        if max_lateral <= half_lane:
            return 1.0
        ratio = (lateral_dist - half_lane) / (max_lateral - half_lane)
        return round(max(0.0, 1.0 - ratio), 4)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def score(self, detections: List[DetectionResult]) -> List[RiskScore]:
        """Compute risk scores for a list of detections.

        Args:
            detections: Output from :class:`~detection.detector.YOLOv8Detector`.

        Returns:
            list[RiskScore]: One :class:`RiskScore` per detection, sorted by
            descending score (highest risk first).
        """
        scored: List[RiskScore] = []
        for det in detections:
            cc = self._class_criticality(det.class_name)
            pw = self._proximity_weight(det.distance_estimate)
            lw = self._lane_weight(det.bbox)
            # Combine: class + proximity dominate; confidence modulates; lane weights
            raw = cc * pw * det.confidence * lw
            final_score = round(min(1.0, raw), 4)
            scored.append(
                RiskScore(
                    detection=det,
                    class_criticality=cc,
                    proximity_weight=pw,
                    lane_weight=lw,
                    score=final_score,
                )
            )

        scored.sort(key=lambda rs: rs.score, reverse=True)
        return scored
