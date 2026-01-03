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
