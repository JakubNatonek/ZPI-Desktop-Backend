"""Add reservation_type and group_names to rapla_imported_reservations

Revision ID: 20260511_0001
Revises: 20260510_0003
Create Date: 2026-05-11 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260511_0001"
down_revision = "20260510_0003"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    existing_cols = {col["name"] for col in inspector.get_columns("rapla_imported_reservations")}

    if "reservation_type" not in existing_cols:
        op.add_column(
            "rapla_imported_reservations",
            sa.Column("reservation_type", sa.String(length=50), nullable=False, server_default="dezyderata"),
        )

    if "group_names" not in existing_cols:
        op.add_column(
            "rapla_imported_reservations",
            sa.Column("group_names", sa.JSON(), nullable=True),
        )


def downgrade():
    op.drop_column("rapla_imported_reservations", "group_names")
    op.drop_column("rapla_imported_reservations", "reservation_type")
