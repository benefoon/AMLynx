from typing import Iterable
import pandas as pd
from sqlalchemy import select
from src.db.session import SessionLocal
from src.db.models import Transaction
from datetime import datetime, timezone
import numpy as np

def fetch_transactions(limit: int = 10000) -> pd.DataFrame:
    with SessionLocal() as session:
        q = select(Transaction).limit(limit)
        rows = session.execute(q).scalars().all()
        data = []
        for r in rows:
            data.append({
                "tx_id": r.tx_id,
                "src_account": r.src_account,
                "dst_account": r.dst_account,
                "amount": float(r.amount),
                "currency": r.currency,
                "channel": r.channel or "unknown",
                "merchant_code": r.merchant_code,
                "tx_ts": r.tx_ts.replace(tzinfo=timezone.utc).isoformat() if r.tx_ts else None,
            })
        df = pd.DataFrame(data)
        return df

def compute_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # amount z-score per src_account (simple, uses global mean/std for dev)
    df["amount_log"] = np.log1p(df["amount"].astype(float))
    global_mean = df["amount_log"].mean()
    global_std = df["amount_log"].std(ddof=0) or 1.0
    df["amount_zscore"] = (df["amount_log"] - global_mean) / global_std
    # time features
    df["tx_ts"] = pd.to_datetime(df["tx_ts"])
    df["hour"] = df["tx_ts"].dt.hour
    df["dayofweek"] = df["tx_ts"].dt.dayofweek
    # simple engineered feature: large_transaction
    df["is_large"] = (df["amount"] > 10000).astype(int)
    return df

def build_feature_table(out_path: str = "data/features.csv"):
    df = fetch_transactions(limit=20000)
    df_feat = compute_basic_features(df)
    df_feat.to_csv(out_path, index=False)
    return out_path
