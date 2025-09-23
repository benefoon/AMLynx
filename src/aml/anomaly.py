from __future__ import annotations

from typing import Protocol, Sequence, Tuple
import numpy as np

try:
    from sklearn.ensemble import IsolationForest
except Exception as e:  # pragma: no cover
    IsolationForest = None  # type: ignore


class AnomalyModel(Protocol):
    def fit(self, X: np.ndarray) -> "AnomalyModel": ...
    def score(self, X: np.ndarray) -> np.ndarray: ...
    def predict(self, X: np.ndarray) -> np.ndarray: ...


class IsoForestModel:
    """Lightweight wrapper to keep sklearn dependency local and swappable."""
    def __init__(self, n_estimators: int = 200, contamination: float = 0.01, random_state: int = 42):
        if IsolationForest is None:
            raise RuntimeError("scikit-learn is required for IsoForestModel")
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state,
        )

    def fit(self, X: np.ndarray) -> "IsoForestModel":
        self.model.fit(X)
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        # Higher is more normal in IsolationForest; invert to get anomaly score in [0, +)
        raw = self.model.score_samples(X)
        return (raw.max() - raw).astype(np.float32)

    def predict(self, X: np.ndarray) -> np.ndarray:
        # 1 -> normal, -1 -> anomaly (sklearn); map to {0,1} where 1 means anomaly
        y = self.model.predict(X)
        return (y == -1).astype(np.int8)


def train_val_split(X: np.ndarray, frac: float = 0.8) -> Tuple[np.ndarray, np.ndarray]:
    n = len(X)
    k = int(n * frac)
    return X[:k], X[k:]
