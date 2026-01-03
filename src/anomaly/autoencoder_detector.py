"""Autoencoder-based anomaly detector using PyTorch."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any
import numpy as np
import numpy.typing as npt

from .detector import DetectorBase
from core.logging import logger


class AutoencoderDetector(DetectorBase):
    """Deep learning anomaly detector based on reconstruction error."""

    def __init__(
        self,
        input_dim: int,
        hidden_dims: list[int] | None = None,
        epochs: int = 100,
        batch_size: int = 64,
        lr: float = 1e-3,
        threshold_percentile: float = 95.0,
    ) -> None:
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims or [128, 64, 32]
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.threshold_percentile = threshold_percentile

        self.scaler = StandardScaler()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._build_model().to(self.device)
        self.threshold: float = 0.0

        logger.info("AutoencoderDetector initialized on device: %s", self.device)

    def _build_model(self) -> nn.Module:
        encoder_dims = [self.input_dim] + self.hidden_dims
        decoder_dims = encoder_dims[::-1]

        layers: list[nn.Module] = []
        for i in range(len(encoder_dims) - 1):
            layers.extend([nn.Linear(encoder_dims[i], encoder_dims[i + 1]), nn.ReLU()])
        for i in range(1, len(decoder_dims)):
            layers.extend([nn.Linear(decoder_dims[i - 1], decoder_dims[i]), nn.ReLU()])
        layers.append(nn.Linear(decoder_dims[-1], self.input_dim))

        return nn.Sequential(*layers)

    def train(self, X: npt.NDArray[np.float64]) -> None:
        """Train only on presumably normal data."""
        try:
            X_scaled = self.scaler.fit_transform(X)
            dataset = torch.tensor(X_scaled, dtype=torch.float32)
            loader = torch.utils.data.DataLoader(
                dataset, batch_size=self.batch_size, shuffle=True
            )

            criterion = nn.MSELoss()
            optimizer = optim.Adam(self.model.parameters(), lr=self.lr)

            self.model.train()
            for epoch in range(self.epochs):
                epoch_loss = 0.0
                for batch in loader:
                    batch = batch.to(self.device)
                    recon = self.model(batch)
                    loss = criterion(recon, batch)

                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    epoch_loss += loss.item()

                if (epoch + 1) % 20 == 0:
                    logger.debug("Autoencoder epoch %d/%d - loss: %.6f", epoch + 1, self.epochs, epoch_loss / len(loader))

            # Compute threshold on training reconstruction errors
            with torch.no_grad():
                recon_errors = torch.mean((self.model(dataset.to(self.device)) - dataset.to(self.device)) ** 2, dim=1)
                self.threshold = torch.quantile(recon_errors, self.threshold_percentile / 100.0).item()

            logger.info("Autoencoder training completed. Threshold set to %.6f", self.threshold)

        except Exception as e:
            logger.error("Error during autoencoder training: %s", e)
            raise

    def predict(self, X: npt.NDArray[np.float64]) -> npt.NDArray[np.int32]:
        return (self.score(X) > self.threshold).astype(np.int32)

    def score(self, X: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        try:
            X_scaled = self.scaler.transform(X)
            X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(self.device)
            with torch.no_grad():
                recon = self.model(X_tensor)
                errors = torch.mean((recon - X_tensor) ** 2, dim=1)
            return errors.cpu().numpy()
        except Exception as e:
            logger.error("Error during autoencoder scoring: %s", e)
            raise

    def explain(self, X: npt.NDArray[np.float64]) -> list[Dict[str, Any]]:
        # Simple feature contribution based on reconstruction error
        X_scaled = self.scaler.transform(X)
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            recon = self.model(X_tensor)
            contrib = torch.abs(X_tensor - recon).cpu().numpy()
        return [{"feature_importance": dict(enumerate(row))} for row in contrib]
