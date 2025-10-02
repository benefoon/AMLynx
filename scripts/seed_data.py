from datetime import datetime, timedelta, timezone
from random import random, randint, choice
from sqlalchemy.orm import Session
from db.session import SessionLocal, engine
from db.models import Base, Account, Transaction

Base.metadata.create_all(bind=engine)

countries = ["DE","FI","SE","AE","IR","US","GB","FR","IT","ES"]

def seed(n_accounts=20, tx_per_account=50):
    with SessionLocal() as db:
        # accounts
        accts = []
        for i in range(n_accounts):
            a = Account(external_id=f"acct_{i:04d}", country=choice(countries))
            db.add(a); accts.append(a)
        db.flush()

        # transactions
        now = datetime.now(timezone.utc)
        for a in accts:
            t0 = now - timedelta(days=5)
            for _ in range(tx_per_account):
                t0 += timedelta(minutes=randint(10, 240))
                amt = abs(np_random_amount())
                db.add(Transaction(
                    account_id=a.id, amount=amt, currency="EUR",
                    country=choice(countries), timestamp=t0, metadata={}
                ))
        db.commit()

def np_random_amount():
    # heavy tail distribution
    from numpy.random import lognormal
    return float(lognormal(mean=4.5, sigma=1.0))

if __name__ == "__main__":
    seed()
