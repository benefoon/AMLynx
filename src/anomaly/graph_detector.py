"""Graph-based anomaly detection for transaction networks."""

from __future__ import annotations

import networkx as nx
import numpy as np
import numpy.typing as npt
from typing import Dict, Any
from pandas import DataFrame

from .detector import DetectorBase
from core.logging import logger


class GraphDetector(DetectorBase):
    """Detect suspicious patterns using transaction graph analysis."""

    def __init__(self, centrality_threshold: float = 0.8, cycle_risk_factor: float = 2.0):
        self.centrality_threshold = centrality_threshold
        self.cycle_risk_factor = cycle_risk_factor
        self.G = nx.DiGraph()

    def train(self, transactions: DataFrame) -> None:
        """Build graph from historical transactions."""
        self.G.clear()
        for _, row in transactions.iterrows():
            self.G.add_edge(row["sender_id"], row["receiver_id"], amount=row["amount"], tx_id=row["id"])
        logger.info("Transaction graph built with %d nodes and %d edges", self.G.number_of_nodes(), self.G.number_of_edges())

    def predict(self, X: npt.NDArray[np.float64]) -> npt.NDArray[np.int32]:
        return (self.score(X) > 0.5).astype(np.int32)

    def score(self, X: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        # X expected to have transaction-level features including sender/receiver ids
        # This is a simplified version - in practice you'd map X to graph nodes
        scores = np.zeros(len(X))
        centrality = nx.degree_centrality(self.G)

        for i, row in enumerate(X):
            sender = int(row[0])  # assume first columns are ids - adjust as needed
            receiver = int(row[1])
            score = 0.0
            if centrality.get(sender, 0) > self.centrality_threshold:
                score += 0.4
            if centrality.get(receiver, 0) > self.centrality_threshold:
                score += 0.4
            if nx.has_path(self.G, receiver, sender):  # possible cycle
                score += self.cycle_risk_factor * 0.2
            scores[i] = min(score, 1.0)

        return scores

    def explain(self, X: npt.NDArray[np.float64]) -> list[Dict[str, Any]]:
        return [{"reason": "High centrality or cycle involvement"}] * len(X)
