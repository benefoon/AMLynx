from alembic import op
import sqlalchemy as sa
from datetime import date, timedelta

# revision identifiers, used by Alembic.
revision = "0004_time_partitioning"
down_revision = "0003_operational_hardening"
branch_labels = None
depends_on = None

def _month_bounds(d: date):
    first = d.replace(day=1)
    if first.month == 12:
        nxt = first.replace(year=first.year+1, month=1)
    else:
        nxt = first.replace(month=first.month+1)
    return first, nxt

def _create_month_parts(table: str, col: str, months_back=12, months_forward=3):
    # create partitions for a range around today
    today = date.today().replace(day=1)
    # back
    cur = today
    for _ in range(months_back):
        cur = (cur.replace(day=1) - timedelta(days=1)).replace(day=1)
    # now iterate forward until forward end
    end = today
    for _ in range(months_forward):
        if end.month == 12:
            end = end.replace(year=end.year+1, month=1)
        else:
            end = end.replace(month=end.month+1)
    # step months
    parts = []
    cursor = cur
    while cursor <= end:
        lo, hi = _month_bounds(cursor)
        name = f"{table}_p_{lo.strftime('%Y_%m')}"
        parts.append((name, lo, hi))
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year+1, month=1)
        else:
            cursor = cursor.replace(month=cursor.month+1)
    for name, lo, hi in parts:
        op.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = '{name}') THEN
                    CREATE TABLE {name} PARTITION OF {table}
                    FOR VALUES FROM ('{lo.isoformat()}') TO ('{hi.isoformat()}');
                END IF;
            END $$;
        """)

def upgrade() -> None:
    # TRANSACTIONS: create new partitioned table
    op.execute("""
        ALTER TABLE transactions RENAME TO transactions_old;
        CREATE TABLE transactions (
            tx_id uuid PRIMARY KEY,
            src_account uuid NOT NULL,
            dst_account uuid NOT NULL,
            amount numeric(18,4) NOT NULL,
            currency varchar(3) NOT NULL DEFAULT 'USD',
            channel varchar(32),
            merchant_code varchar(20),
            tx_ts timestamp NOT NULL DEFAULT NOW(),
            ip_hash varchar(128),
            geo jsonb,
            raw_payload jsonb,
            processed boolean NOT NULL DEFAULT false
        ) PARTITION BY RANGE (tx_ts);
    """)
    # move data
    op.execute("""
        INSERT INTO transactions
        SELECT * FROM transactions_old;
    """)
    # recreate FKs & indexes comparable to old
    op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_tx_ts ON transactions (tx_ts)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_src ON transactions (src_account)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_dst ON transactions (dst_account)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_currency ON transactions (currency)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_src_ts ON transactions (src_account, tx_ts DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_dst_ts ON transactions (dst_account, tx_ts DESC)")
    # create partitions
    _create_month_parts("transactions", "tx_ts")

    # ALERTS
    op.execute("""
        ALTER TABLE alerts RENAME TO alerts_old;
        CREATE TABLE alerts (
            alert_id uuid PRIMARY KEY,
            tx_id varchar(64) NOT NULL,
            src_account varchar(64) NOT NULL,
            dst_account varchar(64) NOT NULL,
            amount numeric(18,4) NOT NULL,
            currency varchar(3) NOT NULL,
            risk_score numeric(6,5) NOT NULL CHECK (risk_score >= 0 AND risk_score <= 1),
            model_score numeric(6,5) NOT NULL CHECK (model_score >= 0 AND model_score <= 1),
            rule_score numeric(6,5) NOT NULL CHECK (rule_score >= 0 AND rule_score <= 1),
            priority integer NOT NULL DEFAULT 0 CHECK (priority >= 0 AND priority <= 100),
            tags jsonb NOT NULL DEFAULT '[]'::jsonb,
            explanation jsonb NOT NULL,
            status alert_status_enum NOT NULL DEFAULT 'new',
            created_at timestamp NOT NULL DEFAULT NOW(),
            assigned_to varchar(128)
        ) PARTITION BY RANGE (created_at);
    """)
    op.execute("INSERT INTO alerts SELECT * FROM alerts_old;")
    # indexes
    op.execute("CREATE INDEX IF NOT EXISTS ix_alerts_created_at ON alerts (created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_alerts_priority ON alerts (priority)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_alerts_tx_id ON alerts (tx_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_alerts_src_account ON alerts (src_account)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_alerts_status ON alerts (status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_alerts_tags_gin ON alerts USING GIN (tags)")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_alerts_new_priority_desc
                  ON alerts (priority DESC, created_at DESC) WHERE status = 'new'""")
    # partitions
    _create_month_parts("alerts", "created_at")

    # drop old
    op.execute("DROP TABLE transactions_old")
    op.execute("DROP TABLE alerts_old")

def downgrade() -> None:
    # revert ALERTS
    op.execute("ALTER TABLE alerts RENAME TO alerts_parted")
    op.execute("""
        CREATE TABLE alerts (
            alert_id uuid PRIMARY KEY,
            tx_id varchar(64) NOT NULL,
            src_account varchar(64) NOT NULL,
            dst_account varchar(64) NOT NULL,
            amount numeric(18,4) NOT NULL,
            currency varchar(3) NOT NULL,
            risk_score numeric(6,5) NOT NULL,
            model_score numeric(6,5) NOT NULL,
            rule_score numeric(6,5) NOT NULL,
            priority integer NOT NULL DEFAULT 0,
            tags jsonb NOT NULL DEFAULT '[]'::jsonb,
            explanation jsonb NOT NULL,
            status alert_status_enum NOT NULL DEFAULT 'new',
            created_at timestamp NOT NULL DEFAULT NOW(),
            assigned_to varchar(128)
        );
    """)
    op.execute("INSERT INTO alerts SELECT * FROM alerts_parted")
    op.execute("DROP TABLE alerts_parted CASCADE")

    # revert TRANSACTIONS
    op.execute("ALTER TABLE transactions RENAME TO transactions_parted")
    op.execute("""
        CREATE TABLE transactions (
            tx_id uuid PRIMARY KEY,
            src_account uuid NOT NULL,
            dst_account uuid NOT NULL,
            amount numeric(18,4) NOT NULL,
            currency varchar(3) NOT NULL DEFAULT 'USD',
            channel varchar(32),
            merchant_code varchar(20),
            tx_ts timestamp NOT NULL DEFAULT NOW(),
            ip_hash varchar(128),
            geo jsonb,
            raw_payload jsonb,
            processed boolean NOT NULL DEFAULT false
        );
    """)
    op.execute("INSERT INTO transactions SELECT * FROM transactions_parted")
    op.execute("DROP TABLE transactions_parted CASCADE")

    # re-create base indexes
    op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_tx_ts ON transactions (tx_ts)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_src ON transactions (src_account)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_dst ON transactions (dst_account)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_currency ON transactions (currency)")
