"""
Safety-critical decision-making module.

Converts a list of :class:`~decision.risk_scorer.RiskScore` objects into one
of three driving commands:

* **STOP** – immediate halt; issued when a critically dangerous object is
  detected within the ego lane or when multiple high-risk objects are present.
* **SLOW** – reduce speed and proceed cautiously.
* **GO**  – normal driving; no significant hazards detected.

Decision thresholds are configurable so the system can be tuned to different
risk tolerances (e.g. more conservative in urban scenarios).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List

from .risk_scorer import RiskScore

logger = logging.getLogger(__name__)


class DrivingCommand(Enum):
    """High-level driving command output."""

    GO = "GO"
    SLOW = "SLOW"
    STOP = "STOP"


@dataclass
class DecisionOutput:
    """Full output of the decision-making pipeline for one frame.

    Attributes:
        command (DrivingCommand): The recommended driving action.
        max_risk_score (float): Highest individual risk score in the frame.
        aggregate_risk (float): Weighted aggregate of all risk scores.
        primary_hazard (RiskScore | None): The highest-risk detection, if any.
        all_scores (list[RiskScore]): All scored detections (descending order).
        reason (str): Human-readable explanation of the decision.
    """

    command: DrivingCommand
    max_risk_score: float
    aggregate_risk: float
    primary_hazard: "RiskScore | None"
    all_scores: List[RiskScore] = field(default_factory=list)
    reason: str = ""


class DecisionMaker:
    """Convert risk scores into STOP / SLOW / GO driving commands.

    The decision logic uses two thresholds:

    * If the *maximum individual risk score* exceeds ``stop_threshold``, or if
      the *aggregate risk* (sum of top-N scores) exceeds ``aggregate_stop_threshold``,
      issue **STOP**.
    * If the maximum score exceeds ``slow_threshold`` (but not the stop
      threshold), issue **SLOW**.
    * Otherwise issue **GO**.

    Args:
        stop_threshold (float): Maximum single-object risk score above which
            STOP is issued (default 0.65).
        slow_threshold (float): Maximum single-object risk score above which
            SLOW is issued (default 0.30).
        aggregate_stop_threshold (float): Sum of the top ``aggregate_top_n``
            risk scores above which STOP is also issued (default 1.20).
        aggregate_top_n (int): Number of top scores to sum for the aggregate
            check (default 3).
    """

    def __init__(
        self,
        stop_threshold: float = 0.65,
        slow_threshold: float = 0.30,
        aggregate_stop_threshold: float = 1.20,
        aggregate_top_n: int = 3,
    ) -> None:
        if not (0.0 < slow_threshold < stop_threshold <= 1.0):
            raise ValueError(
                "Thresholds must satisfy 0 < slow_threshold < stop_threshold ≤ 1"
            )
        self.stop_threshold = stop_threshold
        self.slow_threshold = slow_threshold
        self.aggregate_stop_threshold = aggregate_stop_threshold
        self.aggregate_top_n = aggregate_top_n

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def decide(self, risk_scores: List[RiskScore]) -> DecisionOutput:
        """Derive a driving command from a list of risk-scored detections.

        Args:
            risk_scores: Output of :meth:`~decision.risk_scorer.RiskScorer.score`.

        Returns:
            :class:`DecisionOutput` with the recommended command and metadata.
        """
        if not risk_scores:
            return DecisionOutput(
                command=DrivingCommand.GO,
                max_risk_score=0.0,
                aggregate_risk=0.0,
                primary_hazard=None,
                all_scores=[],
                reason="No objects detected; path is clear.",
            )

        # risk_scores is already sorted descending
        top = risk_scores[0]
        max_score = top.score
        aggregate_risk = round(
            sum(rs.score for rs in risk_scores[: self.aggregate_top_n]), 4
        )

        if max_score >= self.stop_threshold or aggregate_risk >= self.aggregate_stop_threshold:
            cmd = DrivingCommand.STOP
            reason = (
                f"STOP: high-risk object '{top.detection.class_name}' detected "
                f"(score={max_score:.3f}, aggregate={aggregate_risk:.3f})."
            )
        elif max_score >= self.slow_threshold:
            cmd = DrivingCommand.SLOW
            reason = (
                f"SLOW: moderate-risk object '{top.detection.class_name}' detected "
                f"(score={max_score:.3f})."
            )
        else:
            cmd = DrivingCommand.GO
            reason = (
                f"GO: highest risk score is {max_score:.3f}, below slow threshold "
                f"({self.slow_threshold})."
            )

        logger.info(reason)

        return DecisionOutput(
            command=cmd,
            max_risk_score=max_score,
            aggregate_risk=aggregate_risk,
            primary_hazard=top,
            all_scores=risk_scores,
            reason=reason,
        )
