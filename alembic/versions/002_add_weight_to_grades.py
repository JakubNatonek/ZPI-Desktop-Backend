"""add weight to grade_records

Revision ID: 002_add_weight_to_grades
Revises: 001_add_is_blocked
Create Date: 2025-01-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "002_add_weight_to_grades"
down_revision: Union[str, None] = "001_add_is_blocked"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("grade_records", sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"))


def downgrade() -> None:
    op.drop_column("grade_records", "weight")
