"""Ensemble aggregation for multiple anomaly detectors."""

from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
import numpy.typing as npt
from sklearn.ensemble import StackingClassifier

from core.logging import logger
from anomaly.detector import DetectorBase


class EnsembleAggregator:
    """Combine multiple anomaly detectors with learned weights."""

    def __init__(self, detectors: List[DetectorBase], method: str = "weighted_avg"):
        self.detectors = detectors
        self.method = method
        self.weights: npt.NDArray[np.float64] | None = None

    def fit_weights(self, X: npt.NDArray[np.float64], y: npt.NDArray[np.int32]) -> None:
        scores = np.column_stack([d.score(X) for d in self.detectors])
        # Simple logistic regression for weights
        from sklearn.linear_model import LogisticRegression
        clf = LogisticRegression().fit(scores, y)
        self.weights = clf.coef_[0]
        self.weights = np.abs(self.weights) / np.sum(np.abs(self.weights))
        logger.info("Ensemble weights fitted: %s", self.weights)

    def score(self, X: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        scores = np.column_stack([d.score(X) for d in self.detectors])
        if self.weights is not None:
            return np.dot(scores, self.weights)
        return np.mean(scores, axis=1)

    def explain(self, X: npt.NDArray[np.float64]) -> list[Dict[str, Any]]:
        individual_expls = [d.explain(X) for d in self.detectors]
        return [
            {
                "ensemble_score": float(self.score(X[i:i+1])[0]),
                "contributing_detectors": [
                    {"name": d.__class__.__name__, "score": d.score(X[i:i+1])[0]}
                    for d in self.detectors
                ]
            }
            for i in range(len(X))
        ]
