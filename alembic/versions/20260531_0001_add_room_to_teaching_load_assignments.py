"""add room to teaching load assignments

Revision ID: 20260531_0001
Revises: fca1e8594660
Create Date: 2026-05-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260531_0001"
down_revision: Union[str, Sequence[str], None] = "fca1e8594660"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("teaching_load_assignments", sa.Column("room_id", sa.Integer(), nullable=True))
    op.create_index(
        "ix_teaching_load_assignments_room_id",
        "teaching_load_assignments",
        ["room_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_teaching_load_assignments_room_id_room",
        "teaching_load_assignments",
        "room",
        ["room_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_teaching_load_assignments_room_id_room",
        "teaching_load_assignments",
        type_="foreignkey",
    )
    op.drop_index("ix_teaching_load_assignments_room_id", table_name="teaching_load_assignments")
    op.drop_column("teaching_load_assignments", "room_id")
