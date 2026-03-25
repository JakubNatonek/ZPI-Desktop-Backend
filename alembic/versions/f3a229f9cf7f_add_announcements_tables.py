"""add announcements tables

Revision ID: f3a229f9cf7f
Revises: d9b13fa57a21
Create Date: 2026-03-25 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f3a229f9cf7f"
down_revision: Union[str, Sequence[str], None] = "d9b13fa57a21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "announcements",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("(now() at time zone 'utc')")),
    )
    op.create_index("ix_announcements_id", "announcements", ["id"], unique=False)
    op.create_index("ix_announcements_author_id", "announcements", ["author_id"], unique=False)

    op.create_table(
        "announcement_seen",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("announcement_id", sa.Integer(), sa.ForeignKey("announcements.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("(now() at time zone 'utc')")),
        sa.UniqueConstraint("announcement_id", "user_id", name="uq_announcement_seen_announcement_user"),
    )
    op.create_index("ix_announcement_seen_id", "announcement_seen", ["id"], unique=False)
    op.create_index("ix_announcement_seen_announcement_id", "announcement_seen", ["announcement_id"], unique=False)
    op.create_index("ix_announcement_seen_user_id", "announcement_seen", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_announcement_seen_user_id", table_name="announcement_seen")
    op.drop_index("ix_announcement_seen_announcement_id", table_name="announcement_seen")
    op.drop_index("ix_announcement_seen_id", table_name="announcement_seen")
    op.drop_table("announcement_seen")

    op.drop_index("ix_announcements_author_id", table_name="announcements")
    op.drop_index("ix_announcements_id", table_name="announcements")
    op.drop_table("announcements")
