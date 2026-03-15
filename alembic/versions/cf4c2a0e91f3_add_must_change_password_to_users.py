"""add must_change_password to users

Revision ID: cf4c2a0e91f3
Revises: 3be3a8d2e379
Create Date: 2026-03-15 12:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cf4c2a0e91f3"
down_revision: Union[str, Sequence[str], None] = "3be3a8d2e379"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("users", "must_change_password", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "must_change_password")
