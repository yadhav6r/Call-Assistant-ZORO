"""Add persistent login attempt limits for private owner authentication."""

from alembic import op
import sqlalchemy as sa

revision = "0004_private_owner_auth"
down_revision = "0003_simulated_calls"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "login_attempt_limits",
        sa.Column("bucket_hash", sa.String(length=64), primary_key=True),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_login_attempt_limits_window",
        "login_attempt_limits",
        ["window_started_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_login_attempt_limits_window", table_name="login_attempt_limits")
    op.drop_table("login_attempt_limits")
