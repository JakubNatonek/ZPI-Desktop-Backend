"""Add room_names, teacher_names, semester_names to rapla_imported_reservations

Revision ID: 20260510_0002
Revises: 20260510_0001
Create Date: 2026-05-10 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260510_0002"
down_revision = "20260510_0001"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    existing_cols = {col["name"] for col in inspector.get_columns("rapla_imported_reservations")}

    if "room_names" not in existing_cols:
        op.add_column("rapla_imported_reservations", sa.Column("room_names", sa.JSON(), nullable=True))
    if "teacher_names" not in existing_cols:
        op.add_column("rapla_imported_reservations", sa.Column("teacher_names", sa.JSON(), nullable=True))
    if "semester_names" not in existing_cols:
        op.add_column("rapla_imported_reservations", sa.Column("semester_names", sa.JSON(), nullable=True))


def downgrade():
    op.drop_column("rapla_imported_reservations", "semester_names")
    op.drop_column("rapla_imported_reservations", "teacher_names")
    op.drop_column("rapla_imported_reservations", "room_names")
