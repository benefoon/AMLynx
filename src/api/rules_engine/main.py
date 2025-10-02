from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from db.session import SessionLocal
from db.models import RuleDef
from rules_engine.engine import RuleEngine
from common.config import get_settings
import yaml
from pathlib import Path

router = APIRouter(prefix="/rules", tags=["rules"])
settings = get_settings()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class RuleDefIn(BaseModel):
    name: str
    version: str = "v1"
    config: dict

class RuleDefOut(RuleDefIn):
    id: int

@router.get("/", response_model=List[RuleDefOut])
def list_rules(db: Session = Depends(get_db)):
    rows = db.query(RuleDef).all()
    return [RuleDefOut(id=r.id, name=r.name, version=r.version, config=r.config) for r in rows]

@router.post("/", response_model=RuleDefOut)
def create_rule(rule: RuleDefIn, db: Session = Depends(get_db)):
    row = RuleDef(name=rule.name, version=rule.version, config=rule.config)
    db.add(row); db.commit(); db.refresh(row)
    return RuleDefOut(id=row.id, name=row.name, version=row.version, config=row.config)

@router.post("/export-yaml")
def export_yaml(db: Session = Depends(get_db)):
    rows = db.query(RuleDef).all()
    out = {"rules": [r.config | {"name": r.name} for r in rows]}
    Path(settings.RULES_PATH).write_text(yaml.safe_dump(out, sort_keys=False), encoding="utf-8")
    return {"ok": True, "path": settings.RULES_PATH}

@router.post("/reload")
def reload_rules():
    RuleEngine.from_yaml(settings.RULES_PATH)  # this will validate; you can hot-swap in a DI container
    return {"ok": True}
