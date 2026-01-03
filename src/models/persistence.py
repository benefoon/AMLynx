"""Utilities for saving and loading trained models."""

from __future__ import annotations

import joblib
import torch
from pathlib import Path
from typing import Any

from core.logging import logger


class ModelPersistence:
    @staticmethod
    def save_torch(model: torch.nn.Module, scaler, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"model_state_dict": model.state_dict(), "scaler": scaler}, path)
        logger.info("PyTorch model saved to %s", path)

    @staticmethod
    def load_torch(model_class: type, path: Path, input_dim: int):
        checkpoint = torch.load(path, map_location="cpu")
        model = model_class(input_dim=input_dim)
        model.model.load_state_dict(checkpoint["model_state_dict"])
        model.scaler = checkpoint["scaler"]
        logger.info("PyTorch model loaded from %s", path)
        return model

    @staticmethod
    def save_sklearn(model: Any, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, path)
        logger.info("Scikit-learn model saved to %s", path)

    @staticmethod
    def load_sklearn(path: Path) -> Any:
        model = joblib.load(path)
        logger.info("Scikit-learn model loaded from %s", path)
        return model
