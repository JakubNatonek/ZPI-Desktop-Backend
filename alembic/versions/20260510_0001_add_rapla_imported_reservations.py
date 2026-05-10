"""Add rapla_imported_reservations table

Revision ID: 20260510_0001
Revises: 20260505_0001
Create Date: 2026-05-10 00:01:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260510_0001"
down_revision = "20260505_0001"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if "rapla_imported_reservations" not in inspector.get_table_names():
        op.create_table(
            "rapla_imported_reservations",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("uuid", sa.String(200), nullable=False, unique=True, index=True),
            sa.Column("start_date", sa.String(20), nullable=True),
            sa.Column("start_time", sa.String(20), nullable=True),
            sa.Column("end_date", sa.String(20), nullable=True),
            sa.Column("end_time", sa.String(20), nullable=True),
            sa.Column("repeating_type", sa.String(50), nullable=True),
            sa.Column("repeating_end_date", sa.String(20), nullable=True),
            sa.Column("name", sa.String(500), nullable=True),
            sa.Column("allocate", sa.JSON(), nullable=True),
            sa.Column("room_names", sa.JSON(), nullable=True),
            sa.Column("teacher_names", sa.JSON(), nullable=True),
            sa.Column("semester_names", sa.JSON(), nullable=True),
            sa.Column(
                "last_imported_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )


def downgrade():
    op.drop_table("rapla_imported_reservations")
