from alembic import op

# revision identifiers
revision = "0006_mv_account_daily"
down_revision = "0005_rules_history"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("""
    CREATE MATERIALIZED VIEW IF NOT EXISTS mv_account_daily AS
    WITH tx as (
        SELECT
          date_trunc('day', tx_ts) AS d,
          src_account,
          dst_account,
          amount
        FROM transactions
    )
    SELECT
      d::date as day,
      a as account_id,
      sum_out, n_out, avg_out,
      sum_in, n_in, avg_in,
      CASE WHEN sum_out > 0 THEN sum_in / sum_out ELSE NULL END AS inout_ratio
    FROM (
      SELECT
        d,
        src_account as a,
        COALESCE(SUM(amount),0)::numeric(20,4) as sum_out,
        COUNT(*)::bigint as n_out,
        COALESCE(AVG(amount),0)::numeric(20,4) as avg_out
      FROM tx GROUP BY d, src_account
    ) o
    FULL OUTER JOIN (
      SELECT
        d,
        dst_account as a,
        COALESCE(SUM(amount),0)::numeric(20,4) as sum_in,
        COUNT(*)::bigint as n_in,
        COALESCE(AVG(amount),0)::numeric(20,4) as avg_in
      FROM tx GROUP BY d, dst_account
    ) i USING (d, a)
    WHERE a IS NOT NULL;
    """)
    # indexes for fast queries & CONCURRENT REFRESH support
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_mv_account_daily ON mv_account_daily (day, account_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_mv_account_daily_acc ON mv_account_daily (account_id, day DESC)")

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_mv_account_daily_acc")
    op.execute("DROP INDEX IF EXISTS ux_mv_account_daily")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_account_daily")
