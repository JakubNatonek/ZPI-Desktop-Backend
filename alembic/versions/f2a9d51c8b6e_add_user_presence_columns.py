"""add user presence columns

Revision ID: f2a9d51c8b6e
Revises: e7f3c9a1b2d4
Create Date: 2026-03-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f2a9d51c8b6e"
down_revision: Union[str, Sequence[str], None] = "e7f3c9a1b2d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("is_online", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.alter_column("users", "is_online", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "last_seen_at")
    op.drop_column("users", "is_online")
