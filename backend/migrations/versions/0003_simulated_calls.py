"""Persist development text simulations and their policy decisions."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_simulated_calls"
down_revision = "0002_owner_control_plane"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "calls",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(length=32), nullable=False, server_default="text_simulation"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="active"),
        sa.Column("caller_name", sa.String(length=120), nullable=True),
        sa.Column("caller_phone_e164", sa.String(length=16), nullable=True),
        sa.Column(
            "contact_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("contacts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("availability_mode", sa.String(length=24), nullable=False, server_default="available"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('active', 'ended')", name="ck_calls_status"),
        sa.CheckConstraint("channel = 'text_simulation'", name="ck_calls_channel"),
    )
    op.create_index("ix_calls_user_id", "calls", ["user_id"])

    op.create_table(
        "conversation_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "call_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("calls.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("speaker", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("policy", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("call_id", "sequence", name="uq_conversation_events_call_sequence"),
        sa.CheckConstraint(
            "speaker IN ('assistant', 'caller', 'system')", name="ck_events_speaker"
        ),
    )
    op.create_index("ix_conversation_events_call_id", "conversation_events", ["call_id"])


def downgrade() -> None:
    op.drop_index("ix_conversation_events_call_id", table_name="conversation_events")
    op.drop_table("conversation_events")
    op.drop_index("ix_calls_user_id", table_name="calls")
    op.drop_table("calls")
