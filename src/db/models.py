from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    DateTime,
    Boolean,
    JSON,
    ForeignKey,
    func,
)
from sqlalchemy.orm import declarative_base, relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

def gen_uuid():
    return str(uuid.uuid4())

class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    customer_hash = Column(String(128), nullable=False, index=True)
    kyc_level = Column(Integer, default=0)
    country = Column(String(2), nullable=True)
    opened_at = Column(DateTime, server_default=func.now())
    customer_risk_score = Column(Numeric(5,4), default=0.0)
    metadata = Column(JSON, default={})

    outgoing = relationship("Transaction", back_populates="src_account_rel", foreign_keys="Transaction.src_account")
    incoming = relationship("Transaction", back_populates="dst_account_rel", foreign_keys="Transaction.dst_account")

class Transaction(Base):
    __tablename__ = "transactions"
    tx_id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    src_account = Column(UUID(as_uuid=False), ForeignKey("accounts.account_id"), nullable=False, index=True)
    dst_account = Column(UUID(as_uuid=False), ForeignKey("accounts.account_id"), nullable=False, index=True)
    amount = Column(Numeric(18,4), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    channel = Column(String(32), nullable=True)
    merchant_code = Column(String(20), nullable=True)
    tx_ts = Column(DateTime, server_default=func.now(), index=True)
    ip_hash = Column(String(128), nullable=True)
    geo = Column(JSON, nullable=True)
    raw_payload = Column(JSON, nullable=True)
    processed = Column(Boolean, default=False)

    src_account_rel = relationship("Account", foreign_keys=[src_account])
    dst_account_rel = relationship("Account", foreign_keys=[dst_account])
