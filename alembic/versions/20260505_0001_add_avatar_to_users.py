"""add avatar column to users table

Revision ID: 20260505_0001
Revises: 20260413_0001
Create Date: 2026-05-05 00:01:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "20260505_0001"
down_revision = "20260413_0001"
branch_labels = None
depends_on = None


def _has_column(bind, table_name: str, column_name: str) -> bool:
    inspector = inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def upgrade():
    bind = op.get_bind()
    if not _has_column(bind, "users", "avatar"):
        op.add_column("users", sa.Column("avatar", sa.Text(), nullable=True))


def downgrade():
    bind = op.get_bind()
    if _has_column(bind, "users", "avatar"):
        op.drop_column("users", "avatar")
