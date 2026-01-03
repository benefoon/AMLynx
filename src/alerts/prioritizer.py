"""Prioritize alerts based on risk score and explainability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any
from pandas import DataFrame

from core.logging import logger


@dataclass
class PrioritizedAlert:
    transaction_id: int
    risk_score: float
    primary_reason: str
    confidence: float
    explanation: Dict[str, Any]


class AlertPrioritizer:
    """Sort and enrich alerts for analyst review."""

    def __init__(self, high_risk_threshold: float = 0.8):
        self.high_risk_threshold = high_risk_threshold

    def prioritize(self, alerts_df: DataFrame) -> List[PrioritizedAlert]:
        alerts_df = alerts_df.sort_values("risk_score", ascending=False)

        prioritized: List[PrioritizedAlert] = []
        for _, row in alerts_df.iterrows():
            primary_reason = (
                "High anomaly score from deep learning model"
                if row["anomaly_score"] > 0.7
                else "Rule violation + moderate anomaly"
            )
