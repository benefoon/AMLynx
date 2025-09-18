from typing import Dict, Any, List, Tuple
from pydantic import BaseModel, Field
import operator
import math

OPS = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}

class RuleCondition(BaseModel):
    field: str
    op: str
    value: float

class RuleAction(BaseModel):
    add_risk: float = 0.0
    tag: str | None = None

class Rule(BaseModel):
    id: str
    name: str
    conditions: List[RuleCondition]
    actions: List[RuleAction] = Field(default_factory=list)
    enabled: bool = True

def evaluate_rule(rule: Rule, tx: Dict[str, Any]) -> Tuple[float, List[str]]:
    """
    Evaluate a single rule against transaction features.
    Returns: (risk_delta, tags)
    """
    if not rule.enabled:
        return 0.0, []

    # all conditions must hold (AND semantics)
    for cond in rule.conditions:
        left = tx.get(cond.field)
        if left is None:
            return 0.0, []
        op_func = OPS.get(cond.op)
        if op_func is None:
            return 0.0, []
        try:
            if not op_func(left, cond.value):
                return 0.0, []
        except Exception:
            return 0.0, []

    risk = 0.0
    tags = []
    for act in rule.actions:
        if act.add_risk:
            # ensure risk in [0,1]
            risk = min(1.0, risk + float(act.add_risk))
        if act.tag:
            tags.append(act.tag)
    return risk, tags

def evaluate_rules(rules: List[Rule], tx: Dict[str, Any]) -> Tuple[float, List[str]]:
    """
    Evaluate many rules, sum risk contributions (clamped) and union tags.
    """
    total_risk = 0.0
    tags = []
    for r in rules:
        dr, t = evaluate_rule(r, tx)
        total_risk = min(1.0, total_risk + dr)
        tags.extend(t)
    return total_risk, list(set(tags))
