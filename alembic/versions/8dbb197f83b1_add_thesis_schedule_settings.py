"""add thesis schedule settings

Revision ID: 8dbb197f83b1
Revises: f3a229f9cf7f
Create Date: 2026-03-31 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8dbb197f83b1"
down_revision: Union[str, Sequence[str], None] = "f3a229f9cf7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "thesis_schedule_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tab_visible_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tab_visible_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("topic_submission_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("topic_submission_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("proposal_selection_deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("(now() at time zone 'utc')")),
    )

    op.execute(
        """
        INSERT INTO thesis_schedule_settings (id)
        VALUES (1)
        ON CONFLICT (id) DO NOTHING;
        """
    )


def downgrade() -> None:
    op.drop_table("thesis_schedule_settings")