from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from db.session import SessionLocal
from db.models import Transaction, Account, Alert
from rules_engine.engine import RuleEngine, fetch_account_history
from data.etl import to_frame, latest_feature_row
from anomaly.detector import AnomalyDetector
from common.config import get_settings

router = APIRouter(prefix="/transactions", tags=["transactions"])
settings = get_settings()
_engine = RuleEngine.from_yaml(settings.RULES_PATH)
_detector = AnomalyDetector()

class TxIn(BaseModel):
    account_external_id: str
    amount: float
    currency: str
    country: str
    timestamp: datetime
    metadata: dict = {}
    @field_validator("timestamp")
    @classmethod
    def _utc(cls, v: datetime) -> datetime:
        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)

class ScoreOut(BaseModel):
    transaction_id: int
    final_score: float
    rule_score: float
    anomaly_score: float
    suspicious: bool
    explanation: dict

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/ingest-and-score", response_model=ScoreOut)
def ingest_and_score(tx: TxIn, db: Session = Depends(get_db)) -> ScoreOut:
    # Ensure account
    acct = db.query(Account).filter_by(external_id=tx.account_external_id).first()
    if not acct:
        acct = Account(external_id=tx.account_external_id, country=tx.country)
        db.add(acct); db.flush()

    # Persist transaction
    rec = Transaction(
        account_id=acct.id, amount=tx.amount, currency=tx.currency,
        country=tx.country, timestamp=tx.timestamp, metadata=tx.metadata
    )
    db.add(rec); db.flush()

    # History for rules
    history = fetch_account_history(db, acct.id, hours=72)

    # Rules
    rule_score, outcomes = _engine.evaluate(
        tx={"amount": tx.amount, "country": tx.country, "timestamp": tx.timestamp}, history=history
    )

    # Anomaly features
    df = to_frame([*history, {"amount": tx.amount, "country": tx.country, "timestamp": tx.timestamp}])
    x = latest_feature_row(df)
    _detector.load_or_fit(df.to_numpy())  # initial fit if needed
    anomaly_score = float(_detector.score_one(x))

    final = settings.RULES_WEIGHT * rule_score + settings.ANOMALY_WEIGHT * anomaly_score
    suspicious = final >= settings.ALERT_THRESHOLD

    explanation = {
        "rules": [o.__dict__ for o in outcomes],
        "weights": {"rules": settings.RULES_WEIGHT, "anomaly": settings.ANOMALY_WEIGHT},
    }

    if suspicious:
        alert = Alert(transaction_id=rec.id, final_score=final, rule_score=rule_score,
                      anomaly_score=anomaly_score, explanation=explanation)
        db.add(alert)

    db.commit()
    return ScoreOut(
        transaction_id=rec.id, final_score=final, rule_score=rule_score,
        anomaly_score=anomaly_score, suspicious=suspicious, explanation=explanation
    )
