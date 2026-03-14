"""add admin values to user enums

Revision ID: b1f29f84f6aa
Revises: 8e9e4d7d54a1
Create Date: 2026-03-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b1f29f84f6aa"
down_revision: Union[str, Sequence[str], None] = "8e9e4d7d54a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add `admin` option to role and department PostgreSQL enums."""
    # ALTER TYPE ... ADD VALUE may require autocommit on some PostgreSQL versions.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE user_rola ADD VALUE IF NOT EXISTS 'admin';")
        op.execute("ALTER TYPE user_dzial ADD VALUE IF NOT EXISTS 'admin';")


def downgrade() -> None:
    """No-op: PostgreSQL does not support removing enum values safely."""
    pass
