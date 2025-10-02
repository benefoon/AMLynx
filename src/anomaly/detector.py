from __future__ import annotations
from pathlib import Path
import numpy as np
from sklearn.ensemble import IsolationForest
from joblib import dump, load
from common.config import get_settings

class AnomalyDetector:
    def __init__(self, model: IsolationForest | None = None):
        s = get_settings()
        self.model_dir = Path(s.MODEL_DIR)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.model_dir / "iforest.joblib"
        self.model = model or IsolationForest(
            n_estimators=s.IFOREST_TREES,
            contamination=s.CONTAMINATION,
            random_state=s.RANDOM_STATE,
        )

    def fit(self, X: np.ndarray) -> None:
        self.model.fit(X)
        dump(self.model, self.path)

    def load_or_fit(self, X: np.ndarray) -> None:
        if self.path.exists():
            self.model = load(self.path)
        else:
            self.fit(X)

    def score_one(self, x: np.ndarray) -> float:
        """Return anomaly score in [0..1], higher => more anomalous."""
        # IsolationForest decision_function is higher for normal; invert & squash
        raw = -self.model.decision_function(x.reshape(1, -1))[0]
        # Normalize via sigmoid-ish mapping
        return (1.0 / (1.0 + pow(2.71828, -4 * (raw - 0.5))))
