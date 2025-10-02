import pandas as pd
from rules_engine.engine import RuleEngine
from anomaly.detector import AnomalyDetector
from data.etl import to_frame, latest_feature_row

def test_rules_and_anomaly_integration(tmp_path, monkeypatch):
    # Minimal rules file
    p = tmp_path / "rules.yaml"
    p.write_text("rules:\n  - type: amount_over\n    threshold: 1000\n    weight: 1.0\n", encoding="utf-8")
    monkeypatch.setenv("RULES_PATH", str(p))

    engine = RuleEngine.from_yaml(str(p))
    tx = {"amount": 1500.0, "country": "FI", "timestamp": pd.Timestamp.utcnow()}
    rule_score, outcomes = engine.evaluate(tx, history=[])

    assert rule_score > 0 and any(o.rule == "amount_over" for o in outcomes)

    df = to_frame([{"amount": 1500.0, "country": "FI", "timestamp": pd.Timestamp.utcnow()}])
    x = latest_feature_row(df)
    det = AnomalyDetector()
    det.load_or_fit(df.to_numpy())
    s = det.score_one(x)
    assert 0.0 <= s <= 1.0
