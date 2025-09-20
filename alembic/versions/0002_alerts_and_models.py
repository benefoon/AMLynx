from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0002_alerts_and_models"
down_revision = "0001_init"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "alerts",
        sa.Column("alert_id", UUID(as_uuid=False), primary_key=True),
        sa.Column("tx_id", sa.String(64), nullable=False, index=True),
        sa.Column("src_account", sa.String(64), nullable=False, index=True),
        sa.Column("dst_account", sa.String(64), nullable=False),
        sa.Column("amount", sa.Numeric(18,4), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("risk_score", sa.Numeric(6,5), nullable=False),
        sa.Column("model_score", sa.Numeric(6,5), nullable=False),
        sa.Column("rule_score", sa.Numeric(6,5), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tags", sa.JSON(), server_default=sa.text("'[]'::json")),
        sa.Column("explanation", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="new"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("assigned_to", sa.String(128)),
    )

    op.create_table(
        "model_artifacts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("model_type", sa.String(64), nullable=False),  # autoencoder | isolation_forest
        sa.Column("version", sa.String(64), nullable=False),
        sa.Column("path", sa.String(512), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.UniqueConstraint("model_type", "version", name="uq_model_type_version"),
    )

def downgrade() -> None:
    op.drop_table("model_artifacts")
    op.drop_table("alerts")
