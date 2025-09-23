from __future__ import annotations

from pydantic import BaseModel, Field, condecimal, constr
from typing import Optional, Literal


Currency = constr(pattern=r"^[A-Z]{3}$")


class TransactionIn(BaseModel):
    transaction_id: constr(strip_whitespace=True, min_length=6)
    account_id: constr(strip_whitespace=True, min_length=4)
    amount: condecimal(gt=0)
    currency: Currency
    merchant_category: Optional[constr(strip_whitespace=True, max_length=64)] = None
    channel: Literal["CARD", "WIRE", "ACH", "INTERNAL", "CRYPTO"]
    country: constr(regex=r"^[A-Z]{2}$")
    timestamp_ms: int = Field(..., ge=0)


class ScoreResponse(BaseModel):
    risk_score: float
    rules: float
    anomaly: float
