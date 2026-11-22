"""Owner authentication, availability, and contact control-plane data."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_owner_control_plane"
down_revision = "0001_owner_devices"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(), nullable=False, server_default=""),
    )
    op.alter_column("users", "password_hash", server_default=None)

    op.create_table(
        "auth_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("refresh_token_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])

    op.create_table(
        "availability_states",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("mode", sa.String(), nullable=False, server_default="available"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "routing_policy", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "mode IN ('available', 'busy', 'meeting', 'sleeping', 'driving', 'dnd', 'emergency')",
            name="ck_availability_states_mode",
        ),
    )

    op.create_table(
        "contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("phone_e164", sa.String(length=16), nullable=False),
        sa.Column("category", sa.String(), nullable=False, server_default="unknown"),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("trust_level", sa.String(), nullable=False, server_default="unverified"),
        sa.Column(
            "handling_rule", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "phone_e164", name="uq_contacts_user_phone"),
        sa.CheckConstraint(
            "trust_level IN ('unverified', 'known', 'verified')", name="ck_contacts_trust_level"
        ),
    )
    op.create_index("ix_contacts_user_id", "contacts", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_contacts_user_id", table_name="contacts")
    op.drop_table("contacts")
    op.drop_table("availability_states")
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_column("users", "password_hash")
