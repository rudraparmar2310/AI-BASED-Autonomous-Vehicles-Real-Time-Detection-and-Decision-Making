"""
Tests for the STOP / SLOW / GO decision-making module.
"""

import unittest

from detection.detector import DetectionResult
from decision.decision_maker import DecisionMaker, DecisionOutput, DrivingCommand
from decision.risk_scorer import RiskScore, RiskScorer


def _make_risk_score(score: float, class_name: str = "car") -> RiskScore:
    det = DetectionResult(
        class_id=0,
        class_name=class_name,
        confidence=0.9,
        bbox=(500, 300, 700, 450),
        distance_estimate=15.0,
    )
    return RiskScore(
        detection=det,
        class_criticality=0.75,
        proximity_weight=0.8,
        lane_weight=1.0,
        score=score,
    )


class TestDecisionMakerInitValidation(unittest.TestCase):
    """Ensure invalid threshold combinations are rejected."""

    def test_slow_greater_than_stop_raises(self):
        with self.assertRaises(ValueError):
            DecisionMaker(stop_threshold=0.3, slow_threshold=0.7)

    def test_equal_thresholds_raises(self):
        with self.assertRaises(ValueError):
            DecisionMaker(stop_threshold=0.5, slow_threshold=0.5)

    def test_valid_thresholds_do_not_raise(self):
        dm = DecisionMaker(stop_threshold=0.65, slow_threshold=0.30)
        self.assertEqual(dm.stop_threshold, 0.65)


class TestDecisionMakerCommands(unittest.TestCase):
    """Tests for the decide() method command outputs."""

    def setUp(self):
        self.dm = DecisionMaker(
            stop_threshold=0.65,
            slow_threshold=0.30,
            aggregate_stop_threshold=1.20,
            aggregate_top_n=3,
        )

    def test_go_when_no_detections(self):
        output = self.dm.decide([])
        self.assertEqual(output.command, DrivingCommand.GO)
        self.assertIsNone(output.primary_hazard)

    def test_go_when_low_risk(self):
        scores = [_make_risk_score(0.10), _make_risk_score(0.05)]
        output = self.dm.decide(scores)
        self.assertEqual(output.command, DrivingCommand.GO)

    def test_slow_when_moderate_risk(self):
        scores = [_make_risk_score(0.45), _make_risk_score(0.10)]
        output = self.dm.decide(scores)
        self.assertEqual(output.command, DrivingCommand.SLOW)

    def test_stop_when_high_single_risk(self):
        scores = [_make_risk_score(0.80)]
        output = self.dm.decide(scores)
        self.assertEqual(output.command, DrivingCommand.STOP)

    def test_stop_when_aggregate_exceeds_threshold(self):
        # Three moderate risks that sum above aggregate_stop_threshold
        scores = [_make_risk_score(0.45), _make_risk_score(0.42), _make_risk_score(0.40)]
        output = self.dm.decide(scores)
        # 0.45 + 0.42 + 0.40 = 1.27 > 1.20
        self.assertEqual(output.command, DrivingCommand.STOP)

    def test_boundary_at_stop_threshold(self):
        """Score exactly at the stop threshold should trigger STOP."""
        scores = [_make_risk_score(0.65)]
        output = self.dm.decide(scores)
        self.assertEqual(output.command, DrivingCommand.STOP)

    def test_boundary_just_below_stop_threshold(self):
        """Score just below stop threshold should trigger SLOW (above slow)."""
        scores = [_make_risk_score(0.64)]
        output = self.dm.decide(scores)
        self.assertEqual(output.command, DrivingCommand.SLOW)

    def test_boundary_just_below_slow_threshold(self):
        """Score just below slow threshold should trigger GO."""
        scores = [_make_risk_score(0.29)]
        output = self.dm.decide(scores)
        self.assertEqual(output.command, DrivingCommand.GO)

    def test_output_contains_correct_max_score(self):
        scores = [_make_risk_score(0.55), _make_risk_score(0.30)]
        output = self.dm.decide(scores)
        self.assertAlmostEqual(output.max_risk_score, 0.55, places=4)

    def test_output_primary_hazard_is_highest_score(self):
        scores = [_make_risk_score(0.55), _make_risk_score(0.30)]
        output = self.dm.decide(scores)
        self.assertEqual(output.primary_hazard.score, 0.55)

    def test_reason_string_non_empty(self):
        output = self.dm.decide([_make_risk_score(0.50)])
        self.assertIsInstance(output.reason, str)
        self.assertGreater(len(output.reason), 0)

    def test_all_scores_in_output(self):
        scores = [_make_risk_score(0.55), _make_risk_score(0.30), _make_risk_score(0.10)]
        output = self.dm.decide(scores)
        self.assertEqual(len(output.all_scores), 3)


class TestDecisionMakerIntegration(unittest.TestCase):
    """End-to-end tests: detection → risk scoring → decision."""

    def test_pedestrian_close_in_lane_triggers_stop(self):
        """A pedestrian at 5 m in the ego lane should trigger STOP."""
        det = DetectionResult(
            class_id=0,
            class_name="person",
            confidence=0.95,
            bbox=(580, 200, 700, 600),  # centred, tall → close
            distance_estimate=5.0,
        )
        scorer = RiskScorer(image_width=1280)
        dm = DecisionMaker(stop_threshold=0.65, slow_threshold=0.30)

        risk_scores = scorer.score([det])
        output = dm.decide(risk_scores)
        # score = 1.0 * 1.0 * 0.95 * ~1.0 ≈ 0.95 → STOP
        self.assertEqual(output.command, DrivingCommand.STOP)

    def test_distant_peripheral_car_triggers_go(self):
        """A car far away at the image edge should allow GO."""
        det = DetectionResult(
            class_id=2,
            class_name="car",
            confidence=0.75,
            bbox=(1150, 300, 1270, 400),  # far right
            distance_estimate=48.0,
        )
        scorer = RiskScorer(image_width=1280)
        dm = DecisionMaker(stop_threshold=0.65, slow_threshold=0.30)

        risk_scores = scorer.score([det])
        output = dm.decide(risk_scores)
        self.assertEqual(output.command, DrivingCommand.GO)


if __name__ == "__main__":
    unittest.main()
