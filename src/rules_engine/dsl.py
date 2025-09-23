from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Protocol, Union, Callable

Op = Literal["<", "<=", ">", ">=", "==", "!=", "in", "not_in", "startswith", "endswith", "regex"]

@dataclass(frozen=True)
class Predicate:
    field: str
    op: Op
    value: Any

@dataclass(frozen=True)
class Rule:
    id: str
    any_of: List[Predicate]  # OR semantics
    all_of: List[Predicate]  # AND semantics
    weight: float = 1.0
    description: Optional[str] = None


class FieldGetter(Protocol):
    def __call__(self, data: Dict[str, Any], field: str) -> Any: ...


def default_getter(data: Dict[str, Any], field: str) -> Any:
    cur: Any = data
    for token in field.split("."):
        if isinstance(cur, dict):
            cur = cur.get(token)
        else:
            return None
    return cur


def _cmp(a: Any, op: Op, b: Any) -> bool:
    if op == "<": return a < b
    if op == "<=": return a <= b
    if op == ">": return a > b
    if op == ">=": return a >= b
    if op == "==": return a == b
    if op == "!=": return a != b
    if op == "in": return a in b
    if op == "not_in": return a not in b
    if op == "startswith": return str(a).startswith(str(b))
    if op == "endswith": return str(a).endswith(str(b))
    if op == "regex":
        import re
        return bool(re.search(str(b), str(a)))
    raise ValueError(f"Unsupported op: {op}")


def evaluate(rule: Rule, payload: Dict[str, Any], getter: FieldGetter = default_getter) -> bool:
    any_ok = (not rule.any_of) or any(_cmp(getter(payload, p.field), p.op, p.value) for p in rule.any_of)
    all_ok = all(_cmp(getter(payload, p.field), p.op, p.value) for p in rule.all_of)
    return any_ok and all_ok


def score(rules: List[Rule], payload: Dict[str, Any]) -> float:
    return sum(r.weight for r in rules if evaluate(r, payload))


def from_dict(d: Dict[str, Any]) -> Rule:
    return Rule(
        id=d["id"],
        any_of=[Predicate(**p) for p in d.get("any_of", [])],
        all_of=[Predicate(**p) for p in d.get("all_of", [])],
        weight=float(d.get("weight", 1.0)),
        description=d.get("description"),
    )
