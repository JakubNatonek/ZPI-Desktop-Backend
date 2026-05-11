"""Add reservation_uuid and activity_type to rapla_imported_reservations

Revision ID: 20260511_0002
Revises: 20260511_0001
Create Date: 2026-05-11 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260511_0002"
down_revision = "20260511_0001"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    existing_cols = {col["name"] for col in inspector.get_columns("rapla_imported_reservations")}

    if "reservation_uuid" not in existing_cols:
        op.add_column(
            "rapla_imported_reservations",
            sa.Column("reservation_uuid", sa.String(length=200), nullable=True),
        )
        op.create_index(
            "ix_rapla_imported_reservations_reservation_uuid",
            "rapla_imported_reservations",
            ["reservation_uuid"],
        )

    if "activity_type" not in existing_cols:
        op.add_column(
            "rapla_imported_reservations",
            sa.Column("activity_type", sa.String(length=100), nullable=True),
        )


def downgrade():
    op.drop_index("ix_rapla_imported_reservations_reservation_uuid", table_name="rapla_imported_reservations")
    op.drop_column("rapla_imported_reservations", "reservation_uuid")
    op.drop_column("rapla_imported_reservations", "activity_type")
