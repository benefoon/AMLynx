from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple, Callable
from datetime import timedelta
import yaml
from loguru import logger
from sqlalchemy.orm import Session
from db.models import Transaction
from common.config import get_settings

# ---- Base & Registry ----
class Rule(ABC):
    name: str
    weight: float
    @abstractmethod
    def evaluate(self, tx: Dict[str, Any], history: Iterable[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
        """
        Returns (score, details); 0 <= score.
        details should be a compact explanation for the alert UI.
        """
        ...

_RULES: dict[str, Callable[[dict], Rule]] = {}

def register(name: str):
    def _wrap(ctor: Callable[[dict], Rule]):
        _RULES[name] = ctor
        return ctor
    return _wrap

# ---- Concrete Rules ----
@register("amount_over")
class AmountOver(Rule):
    def __init__(self, cfg: dict):
        self.name = cfg.get("name", "amount_over")
        self.threshold = float(cfg["threshold"])
        self.weight = float(cfg.get("weight", 1.0))
    def evaluate(self, tx, history):
        amt = float(tx.get("amount", 0.0))
        if amt > self.threshold:
            score = (amt - self.threshold) / max(self.threshold, 1.0) * self.weight
            return score, {"threshold": self.threshold, "amount": amt}
        return 0.0, {}

@register("velocity")
class Velocity(Rule):
    def __init__(self, cfg: dict):
        self.name = cfg.get("name", "velocity")
        self.window_hours = int(cfg.get("window_hours", 24))
        self.max_tx = int(cfg.get("max_tx", 10))
        self.weight = float(cfg.get("weight", 1.0))
    def evaluate(self, tx, history):
        from datetime import datetime, timezone
        t_now = tx["timestamp"]
        win_start = t_now - timedelta(hours=self.window_hours)
        cnt = sum(1 for h in history if h["timestamp"] >= win_start)
        if cnt > self.max_tx:
            return (cnt - self.max_tx) / max(self.max_tx, 1) * self.weight, {"count": cnt}
        return 0.0, {}

@register("country_risk")
class CountryRisk(Rule):
    def __init__(self, cfg: dict):
        self.name = cfg.get("name", "country_risk")
        self.high_risk = set(cfg.get("high_risk", []))
        self.weight = float(cfg.get("weight", 1.0))
    def evaluate(self, tx, history):
        c = tx.get("country", "").upper()
        if c in self.high_risk:
            return self.weight, {"country": c}
        return 0.0, {}

# ---- Loader & Evaluator ----
@dataclass
class RuleOutcome:
    rule: str
    score: float
    details: Dict[str, Any]

class RuleEngine:
    def __init__(self, rules: List[Rule]):
        self.rules = rules

    @classmethod
    def from_yaml(cls, path: str) -> "RuleEngine":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        rules_cfg = data.get("rules", [])
        rules = []
        for rc in rules_cfg:
            rtype = rc["type"]
            ctor = _RULES.get(rtype)
            if not ctor:
                raise ValueError(f"Unknown rule type: {rtype}")
            rules.append(ctor(rc))
        logger.info(f"Loaded {len(rules)} rules from {path}")
        return cls(rules)

    def evaluate(self, tx: Dict[str, Any], history: Iterable[Dict[str, Any]]) -> Tuple[float, List[RuleOutcome]]:
        outcomes: List[RuleOutcome] = []
        total = 0.0
        for r in self.rules:
            s, d = r.evaluate(tx, history)
            if s > 0:
                outcomes.append(RuleOutcome(r.name, s, d))
                total += s
        return total, outcomes

# Optional: helper to fetch account history efficiently
def fetch_account_history(db: Session, account_id: int, hours: int = 72) -> List[Dict[str, Any]]:
    from sqlalchemy import select, func
    from datetime import datetime, timedelta, timezone
    from db.models import Transaction
    t_end = datetime.utcnow()
    t_start = t_end - timedelta(hours=hours)
    rows = db.execute(
        select(Transaction).where(
            Transaction.account_id == account_id,
            Transaction.timestamp >= t_start
        ).order_by(Transaction.timestamp.desc())
    ).scalars().all()
    return [dict(
        id=r.id, amount=r.amount, country=r.country, timestamp=r.timestamp, currency=r.currency
    ) for r in rows]
