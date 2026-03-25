"""add thesis proposals

Revision ID: d9b13fa57a21
Revises: 320c4ff63aa7
Create Date: 2026-03-25 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d9b13fa57a21"
down_revision: Union[str, Sequence[str], None] = "320c4ff63aa7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


thesis_proposal_status = sa.Enum("PENDING", "APPROVED", "REJECTED", name="thesis_proposal_status")


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO roles (id, name) VALUES (3, 'student')
        ON CONFLICT (id) DO NOTHING;
        """
    )

    thesis_proposal_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "thesis_proposals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("lecturer_id", sa.Integer(), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_average_grade", sa.Float(), nullable=False, server_default="0"),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("justification", sa.Text(), nullable=False),
        sa.Column("status", thesis_proposal_status, nullable=False, server_default="PENDING"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("(now() at time zone 'utc')")),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_thesis_proposals_id", "thesis_proposals", ["id"], unique=False)
    op.create_index("ix_thesis_proposals_student_id", "thesis_proposals", ["student_id"], unique=False)
    op.create_index("ix_thesis_proposals_lecturer_id", "thesis_proposals", ["lecturer_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_thesis_proposals_lecturer_id", table_name="thesis_proposals")
    op.drop_index("ix_thesis_proposals_student_id", table_name="thesis_proposals")
    op.drop_index("ix_thesis_proposals_id", table_name="thesis_proposals")
    op.drop_table("thesis_proposals")

    thesis_proposal_status.drop(op.get_bind(), checkfirst=True)
