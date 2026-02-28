"""
Tests for the adaptive risk scoring module.
"""

import math
import unittest

from detection.detector import DetectionResult
from decision.risk_scorer import RiskScore, RiskScorer


def _make_detection(
    class_name="car",
    confidence=0.9,
    bbox=(540, 300, 740, 450),
    distance_estimate=None,
    class_id=0,
):
    return DetectionResult(
        class_id=class_id,
        class_name=class_name,
        confidence=confidence,
        bbox=bbox,
        distance_estimate=distance_estimate,
    )


class TestRiskScorerProximityWeight(unittest.TestCase):
    """Tests for the proximity weight function."""

    def setUp(self):
        self.scorer = RiskScorer(image_width=1280)

    def test_critical_distance_gives_weight_one(self):
        w = self.scorer._proximity_weight(5.0)  # within critical zone
        self.assertEqual(w, 1.0)

    def test_safe_distance_gives_weight_zero(self):
        w = self.scorer._proximity_weight(60.0)  # beyond safe distance
        self.assertEqual(w, 0.0)

    def test_midpoint_distance_is_half(self):
        mid = (self.scorer.critical_distance_m + self.scorer.safe_distance_m) / 2
        w = self.scorer._proximity_weight(mid)
        # cos(π/2) = 0, so 0.5*(1+0) = 0.5
        self.assertAlmostEqual(w, 0.5, places=3)

    def test_none_distance_returns_conservative(self):
        w = self.scorer._proximity_weight(None)
        self.assertEqual(w, 0.5)


class TestRiskScorerLaneWeight(unittest.TestCase):
    """Tests for the lateral lane weight function."""

    def setUp(self):
        self.scorer = RiskScorer(image_width=1280, lane_width_fraction=0.33)

    def test_centred_object_has_full_weight(self):
        # Object centred at image centre
        bbox = (540, 300, 740, 450)  # cx ≈ 640
        w = self.scorer._lane_weight(bbox)
        self.assertEqual(w, 1.0)

    def test_far_right_object_has_low_weight(self):
        # Object at the far right edge
        bbox = (1200, 300, 1280, 450)  # cx ≈ 1240
        w = self.scorer._lane_weight(bbox)
        self.assertLess(w, 0.5)

    def test_far_left_object_has_low_weight(self):
        bbox = (0, 300, 80, 450)  # cx ≈ 40
        w = self.scorer._lane_weight(bbox)
        self.assertLess(w, 0.5)


class TestRiskScorerScore(unittest.TestCase):
    """Integration tests for RiskScorer.score()."""

    def setUp(self):
        self.scorer = RiskScorer(image_width=1280)

    def test_empty_input_returns_empty(self):
        self.assertEqual(self.scorer.score([]), [])

    def test_returns_risk_score_instances(self):
        det = _make_detection()
        results = self.scorer.score([det])
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], RiskScore)

    def test_scores_in_range(self):
        dets = [
            _make_detection("person", 0.95, distance_estimate=5.0),
            _make_detection("car", 0.80, distance_estimate=30.0),
            _make_detection("traffic light", 0.60, distance_estimate=60.0),
        ]
        for rs in self.scorer.score(dets):
            self.assertGreaterEqual(rs.score, 0.0)
            self.assertLessEqual(rs.score, 1.0)

    def test_sorted_descending(self):
        dets = [
            _make_detection("traffic light", 0.5, distance_estimate=45.0),
            _make_detection("person", 0.95, distance_estimate=4.0),
            _make_detection("car", 0.80, distance_estimate=20.0),
        ]
        results = self.scorer.score(dets)
        scores = [rs.score for rs in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_closer_object_scores_higher_than_distant(self):
        close_det = _make_detection("car", 0.90, distance_estimate=5.0)
        far_det = _make_detection("car", 0.90, distance_estimate=55.0)
        results = self.scorer.score([close_det, far_det])
        self.assertGreater(results[0].score, results[1].score)

    def test_pedestrian_scores_higher_than_traffic_light_at_same_distance(self):
        ped = _make_detection("person", 0.90, distance_estimate=15.0)
        tl = _make_detection("traffic light", 0.90, distance_estimate=15.0)
        results = self.scorer.score([ped, tl])
        # Person should be ranked first (higher criticality)
        self.assertEqual(results[0].detection.class_name, "person")

    def test_low_confidence_reduces_score(self):
        high_conf = _make_detection("car", 0.95, distance_estimate=10.0)
        low_conf = _make_detection("car", 0.20, distance_estimate=10.0)
        rs_high = self.scorer.score([high_conf])[0].score
        rs_low = self.scorer.score([low_conf])[0].score
        self.assertGreater(rs_high, rs_low)


if __name__ == "__main__":
    unittest.main()
