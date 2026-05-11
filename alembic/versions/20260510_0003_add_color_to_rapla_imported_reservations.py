"""Add color to rapla_imported_reservations

Revision ID: 20260510_0003
Revises: 20260510_0002
Create Date: 2026-05-10 14:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260510_0003"
down_revision = "20260510_0002"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    existing_cols = {col["name"] for col in inspector.get_columns("rapla_imported_reservations")}
    if "color" not in existing_cols:
        op.add_column("rapla_imported_reservations", sa.Column("color", sa.String(length=32), nullable=True))


def downgrade():
    op.drop_column("rapla_imported_reservations", "color")
