from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np

from features.store import FeatureStore
from rules_engine.dsl import Rule, score as rules_score
from aml.anomaly import AnomalyModel


class ScoringPipeline:
    """
    Thin orchestrator that:
      1) fetches point-in-time features,
      2) computes rules score,
      3) adds anomaly score,
      4) returns a single risk score with trace.
    """
    def __init__(self, feature_store: FeatureStore, anomaly_model: Optional[AnomalyModel] = None) -> None:
        self.feature_store = feature_store
        self.anomaly_model = anomaly_model

    def _vectorize(self, payload: Dict[str, Any], feature_names: List[str]) -> np.ndarray:
        feats = [payload.get(n) for n in feature_names]
        feats = [0.0 if (v is None or isinstance(v, str)) else float(v) for v in feats]
        return np.asarray(feats, dtype=np.float32).reshape(1, -1)

    def score(
        self,
        payload: Dict[str, Any],
        rules: List[Rule],
        feature_namespace: str,
        entity_id: str,
        feature_names: List[str],
        anomaly_weight: float = 1.0,
        rules_weight: float = 1.0,
    ) -> Dict[str, Any]:
        cached = self.feature_store.get_features(feature_namespace, entity_id, feature_names)
        enriched = {**payload, **{n.split(":")[-1]: v for n, v in cached.items()}}

        r_score = float(rules_score(rules, enriched))
        a_score = 0.0
        if self.anomaly_model:
            X = self._vectorize(enriched, feature_names)
            a_score = float(self.anomaly_model.score(X)[0])

        total = rules_weight * r_score + anomaly_weight * a_score
        return {
            "risk_score": total,
            "breakdown": {"rules": r_score, "anomaly": a_score},
            "features_used": feature_names,
            "entity_id": entity_id,
        }
