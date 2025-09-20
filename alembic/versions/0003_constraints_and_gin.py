from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_operational_hardening"
down_revision = "0002_alerts_and_models"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1) ENUM for alert status
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'alert_status_enum') THEN CREATE TYPE alert_status_enum AS ENUM ('new','in_review','escalated','closed'); END IF; END $$;")
    # alter column type
    op.execute("""
        ALTER TABLE alerts
        ALTER COLUMN status TYPE alert_status_enum USING status::alert_status_enum
    """)

    # 2) CHECK constraints (bounded probabilities and ranges)
    op.execute("ALTER TABLE alerts ADD CONSTRAINT ck_alerts_risk_score_range CHECK (risk_score >= 0 AND risk_score <= 1)")
    op.execute("ALTER TABLE alerts ADD CONSTRAINT ck_alerts_model_score_range CHECK (model_score >= 0 AND model_score <= 1)")
    op.execute("ALTER TABLE alerts ADD CONSTRAINT ck_alerts_rule_score_range CHECK (rule_score >= 0 AND rule_score <= 1)")
    op.execute("ALTER TABLE alerts ADD CONSTRAINT ck_alerts_priority_range CHECK (priority >= 0 AND priority <= 100)")
    op.execute("ALTER TABLE transactions ADD CONSTRAINT ck_transactions_amount_nonneg CHECK (amount >= 0)")
    op.execute("ALTER TABLE accounts ADD CONSTRAINT ck_accounts_kyc_nonneg CHECK (kyc_level >= 0)")

    # 3) updated_at auto trigger for rules
    op.execute("""
    CREATE OR REPLACE FUNCTION trg_set_updated_at() RETURNS trigger AS $$
    BEGIN
      NEW.updated_at = NOW();
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("DROP TRIGGER IF EXISTS t_rules_updated_at ON rules")
    op.execute("""
    CREATE TRIGGER t_rules_updated_at
    BEFORE UPDATE ON rules
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at()
    """)

    # 4) GIN indexes on JSONB fields for filtering
    op.execute("CREATE INDEX IF NOT EXISTS ix_rules_definition_gin ON rules USING GIN (definition jsonb_path_ops)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_alerts_tags_gin ON alerts USING GIN (tags)")

    # 5) partial index for queueing NEW alerts by priority DESC scan
    op.execute("""CREATE INDEX IF NOT EXISTS ix_alerts_new_priority_desc
                  ON alerts (priority DESC, created_at DESC)
                  WHERE status = 'new'""")

    # 6) helpful composite indexes
    op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_src_ts ON transactions (src_account, tx_ts DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_dst_ts ON transactions (dst_account, tx_ts DESC)")

def downgrade() -> None:
    # drop indexes
    op.execute("DROP INDEX IF EXISTS ix_transactions_dst_ts")
    op.execute("DROP INDEX IF EXISTS ix_transactions_src_ts")
    op.execute("DROP INDEX IF EXISTS ix_alerts_new_priority_desc")
    op.execute("DROP INDEX IF EXISTS ix_alerts_tags_gin")
    op.execute("DROP INDEX IF EXISTS ix_rules_definition_gin")

    # drop trigger & function
    op.execute("DROP TRIGGER IF EXISTS t_rules_updated_at ON rules")
    op.execute("DROP FUNCTION IF EXISTS trg_set_updated_at()")

    # drop checks
    op.execute("ALTER TABLE accounts DROP CONSTRAINT IF EXISTS ck_accounts_kyc_nonneg")
    op.execute("ALTER TABLE transactions DROP CONSTRAINT IF EXISTS ck_transactions_amount_nonneg")
    op.execute("ALTER TABLE alerts DROP CONSTRAINT IF EXISTS ck_alerts_priority_range")
    op.execute("ALTER TABLE alerts DROP CONSTRAINT IF EXISTS ck_alerts_rule_score_range")
    op.execute("ALTER TABLE alerts DROP CONSTRAINT IF EXISTS ck_alerts_model_score_range")
    op.execute("ALTER TABLE alerts DROP CONSTRAINT IF EXISTS ck_alerts_risk_score_range")

    # revert enum to text (safe fallback)
    op.execute("ALTER TABLE alerts ALTER COLUMN status TYPE TEXT")
    op.execute("DROP TYPE IF EXISTS alert_status_enum")
