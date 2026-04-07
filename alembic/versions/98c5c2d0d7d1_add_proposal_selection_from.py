"""add proposal selection start date

Revision ID: 98c5c2d0d7d1
Revises: 8dbb197f83b1
Create Date: 2026-03-31 11:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "98c5c2d0d7d1"
down_revision: Union[str, Sequence[str], None] = "8dbb197f83b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("thesis_schedule_settings", sa.Column("proposal_selection_from", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("thesis_schedule_settings", "proposal_selection_from")