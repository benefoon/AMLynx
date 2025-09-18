import random
from datetime import datetime, timedelta
from decimal import Decimal
from src.db.session import SessionLocal, engine
from src.db.models import Base, Account, Transaction
from sqlalchemy.exc import IntegrityError

def create_schema():
    Base.metadata.create_all(bind=engine)

def seed_accounts(session, n=50):
    accounts = []
    for i in range(n):
        a = Account(
            customer_hash=f"cust_{i:04d}",
            kyc_level=random.choice([0, 1, 2]),
            country=random.choice(["US", "GB", "DE", "IR", "KY", "PA"]),
        )
        session.add(a)
        accounts.append(a)
    session.flush()  # get account ids
    return accounts

def seed_transactions(session, accounts, per_account=20):
    now = datetime.utcnow()
    for acc in accounts:
        for _ in range(per_account):
            dst = random.choice(accounts)
            amt = Decimal(round(random.expovariate(1/2000), 2))
            tx = Transaction(
                src_account=acc.account_id,
                dst_account=dst.account_id,
                amount=amt if amt > 0 else Decimal("1.0"),
                currency="USD",
                channel=random.choice(["wire", "ach", "card"]),
                merchant_code=f"M{random.randint(1000,9999)}",
                tx_ts=now - timedelta(minutes=random.randint(0, 60*24*30)),
                raw_payload={"notes": "seed"},
            )
            session.add(tx)
    session.flush()

def main():
    create_schema()
    with SessionLocal() as session:
        accounts = seed_accounts(session, n=80)
        seed_transactions(session, accounts, per_account=30)
        try:
            session.commit()
            print("Seed complete.")
        except IntegrityError as e:
            session.rollback()
            print("Seed failed:", e)

if __name__ == "__main__":
    main()
