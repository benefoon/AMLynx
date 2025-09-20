from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0005_rules_history"
down_revision = "0004_time_partitioning"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS rules_history (
      id bigserial PRIMARY KEY,
      rule_id varchar(64) NOT NULL,
      action varchar(16) NOT NULL, -- insert | update | delete
      before jsonb,
      after jsonb,
      changed_by varchar(128),
      changed_at timestamp NOT NULL DEFAULT NOW()
    );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_rules_history_rule_id ON rules_history (rule_id, changed_at DESC)")

    # helper to capture current user name if app sets it (optional)
    op.execute("""
    CREATE OR REPLACE FUNCTION get_app_user() RETURNS varchar AS $$
    BEGIN
      BEGIN
        RETURN current_setting('app.user');
      EXCEPTION WHEN others THEN
        RETURN NULL;
      END;
    END; $$ LANGUAGE plpgsql;
    """)

    # trigger to log changes
    op.execute("""
    CREATE OR REPLACE FUNCTION trg_rules_audit() RETURNS trigger AS $$
    DECLARE who varchar;
    BEGIN
      who := get_app_user();
      IF (TG_OP = 'INSERT') THEN
        INSERT INTO rules_history(rule_id, action, before, after, changed_by)
        VALUES (NEW.id, 'insert', NULL, row_to_json(NEW)::jsonb, who);
        RETURN NEW;
      ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO rules_history(rule_id, action, before, after, changed_by)
        VALUES (NEW.id, 'update', row_to_json(OLD)::jsonb, row_to_json(NEW)::jsonb, who);
        RETURN NEW;
      ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO rules_history(rule_id, action, before, after, changed_by)
        VALUES (OLD.id, 'delete', row_to_json(OLD)::jsonb, NULL, who);
        RETURN OLD;
      END IF;
      RETURN NULL;
    END; $$ LANGUAGE plpgsql;
    """)
    op.execute("DROP TRIGGER IF EXISTS t_rules_audit ON rules")
    op.execute("""
    CREATE TRIGGER t_rules_audit
    AFTER INSERT OR UPDATE OR DELETE ON rules
    FOR EACH ROW EXECUTE FUNCTION trg_rules_audit()
    """)

def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS t_rules_audit ON rules")
    op.execute("DROP FUNCTION IF EXISTS trg_rules_audit()")
    op.execute("DROP FUNCTION IF EXISTS get_app_user()")
    op.execute("DROP TABLE IF EXISTS rules_history")
