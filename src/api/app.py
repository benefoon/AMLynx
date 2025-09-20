from fastapi import FastAPI
from pydantic import BaseModel
from src.common.config import get_settings
from src.data.etl import compute_basic_features
from src.rules_engine.engine import Rule, evaluate_rules
from src.scoring.hybrid import fuse_scores, FusionConfig
import yaml
from typing import List

app = FastAPI(title=get_settings().app_name)

# for demo: load example rules from YAML file (in real system: store in DB)
DEFAULT_RULES_YAML = """
- id: r_001
  name: large_to_offshore
  conditions:
    - field: amount
      op: ">"
      value: 10000
  actions:
    - add_risk: 0.6
    - tag: "large_transfer"
- id: r_002
  name: midnight_tx
  conditions:
    - field: hour
      op: "<"
      value: 6
  actions:
    - add_risk: 0.15
    - tag: "odd_hour"
"""

rules_list = [Rule.model_validate(r) for r in yaml.safe_load(DEFAULT_RULES_YAML)]

class ScoreRequest(BaseModel):
    tx_id: str
    amount: float
    currency: str = "USD"
    src_account: str
    dst_account: str
    tx_ts: str  # ISO8601

@app.post("/v1/score")
def score_tx(req: ScoreRequest):
    # build minimal feature dict expected by rules
    feat = {
        "tx_id": req.tx_id,
        "amount": req.amount,
        "currency": req.currency,
        "src_account": req.src_account,
        "dst_account": req.dst_account,
        "tx_ts": req.tx_ts,
        "hour": int(req.tx_ts[11:13]) if len(req.tx_ts) >= 13 else 0,
    }

    rule_score, tags = evaluate_rules(rules_list, feat)
    # placeholder model score: simple heuristic (in prod: call model service)
    model_score = 0.05 + min(0.95, max(0.0, (feat["amount"] / 20000.0)))
    risk = fuse_scores(model_score=model_score, rule_score=rule_score, cfg=FusionConfig())
    return {"tx_id": req.tx_id, "model_score": model_score, "rule_score": rule_score, "risk_score": risk, "tags": tags}
