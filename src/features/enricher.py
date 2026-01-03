"""Advanced feature enrichment for transactions."""

from __future__ import annotations

from pandas import DataFrame
from typing import Dict
import numpy as np

from core.logging import logger


class TransactionEnricher:
    """Add velocity, ratio, and behavioral features."""

    def __init__(self, velocity_windows: list[int] = None):
        self.velocity_windows = velocity_windows or [1, 7, 30]  # days

    def enrich(self, df: DataFrame) -> DataFrame:
        df = df.sort_values(["sender_id", "timestamp"])

        for window in self.velocity_windows:
            df[f"tx_count_{window}d"] = (
                df.groupby("sender_id")["timestamp"]
                .transform(lambda x: x.rolling(f"{window}D", closed="right").count() - 1)
            )
            df[f"tx_amount_sum_{window}d"] = (
                df.groupby("sender_id")["amount"]
                .transform(lambda x: x.rolling(f"{window}D", closed="right").sum() - df["amount"])
            )
            df[f"tx_amount_avg_{window}d"] = df[f"tx_amount_sum_{window}d"] / df[f"tx_count_{window}d"].replace(0, 1)

        df["amount_to_avg_ratio"] = df["amount"] / (df[[f"tx_amount_avg_{w}d" for w in self.velocity_windows]].mean(axis=1) + 1e-8)
        df["is_international"] = (df["sender_country"] != df["receiver_country"]).astype(int)

        logger.info("Transaction enrichment completed with %d new features", len(df.columns) - len(df.columns.drop(df.filter(like="tx_").columns)))
        return df
