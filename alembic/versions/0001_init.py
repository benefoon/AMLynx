from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # accounts
    op.create_table(
        "accounts",
        sa.Column("account_id", UUID(as_uuid=False), primary_key=True),
        sa.Column("customer_hash", sa.String(128), nullable=False),
        sa.Column("kyc_level", sa.Integer(), server_default="0", nullable=False),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("opened_at", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("customer_risk_score", sa.Numeric(5, 4), server_default="0.0", nullable=False),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False),
    )
    op.create_index("ix_accounts_customer_hash", "accounts", ["customer_hash"])
    op.create_index("ix_accounts_country", "accounts", ["country"])

    # transactions
    op.create_table(
        "transactions",
        sa.Column("tx_id", UUID(as_uuid=False), primary_key=True),
        sa.Column("src_account", UUID(as_uuid=False), sa.ForeignKey("accounts.account_id"), nullable=False),
        sa.Column("dst_account", UUID(as_uuid=False), sa.ForeignKey("accounts.account_id"), nullable=False),
        sa.Column("amount", sa.Numeric(18, 4), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("channel", sa.String(32), nullable=True),
        sa.Column("merchant_code", sa.String(20), nullable=True),
        sa.Column("tx_ts", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("ip_hash", sa.String(128), nullable=True),
        sa.Column("geo", JSONB, nullable=True),
        sa.Column("raw_payload", JSONB, nullable=True),
        sa.Column("processed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.create_index("ix_transactions_tx_ts", "transactions", ["tx_ts"])
    op.create_index("ix_transactions_src", "transactions", ["src_account"])
    op.create_index("ix_transactions_dst", "transactions", ["dst_account"])
    op.create_index("ix_transactions_currency", "transactions", ["currency"])

    # rules (CRUD-friendly + audit ساده)
    op.create_table(
        "rules",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("definition", JSONB, nullable=False),  # {"condition": {...}, "actions":[...]}
        sa.Column("enabled", sa
