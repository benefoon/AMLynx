from src.rules_engine.engine import Rule, RuleCondition, RuleAction, evaluate_rule
from datetime import datetime

def test_simple_rule_matches():
    rule = Rule(
        id="t1",
        name="test_large",
        conditions=[RuleCondition(field="amount", op=">", value=1000)],
        actions=[RuleAction(add_risk=0.5, tag="big")],
    )
    tx = {"amount": 1500}
    risk, tags = evaluate_rule(rule, tx)
    assert risk == 0.5
    assert "big" in tags

def test_rule_non_match():
    rule = Rule(
        id="t2",
        name="test_small",
        conditions=[RuleCondition(field="amount", op="<", value=50)],
        actions=[RuleAction(add_risk=0.5, tag="tiny")],
    )
    tx = {"amount": 1500}
    risk, tags = evaluate_rule(rule, tx)
    assert risk == 0.0
    assert tags == []
