"""add delivered_at and read_at columns to messages

Revision ID: e7f3c9a1b2d4
Revises: d4a2f8c1b6e3
Create Date: 2026-03-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e7f3c9a1b2d4"
down_revision: Union[str, Sequence[str], None] = "d4a2f8c1b6e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("messages", sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("messages", sa.Column("read_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("messages", "read_at")
    op.drop_column("messages", "delivered_at")
