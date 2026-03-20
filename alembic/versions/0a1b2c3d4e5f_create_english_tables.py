"""create english-named tables: group, teacher, subject, room

Revision ID: 0a1b2c3d4e5f
Revises: 9f1d6b2c4a77
Create Date: 2026-03-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0a1b2c3d4e5f"
down_revision: Union[str, Sequence[str], None] = "9f1d6b2c4a77"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "group",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("spec", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("studies", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_group_id"), "group", ["id"], unique=False)

    op.create_table(
        "teacher",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("prop", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_teacher_id"), "teacher", ["id"], unique=False)
    op.create_index(op.f("ix_teacher_user_id"), "teacher", ["user_id"], unique=False)

    op.create_table(
        "subject",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("type_show", sa.String(), nullable=True),
        sa.Column("prop_room", sa.String(), nullable=True),
        sa.Column("blocked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("periodic", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subject_id"), "subject", ["id"], unique=False)

    op.create_table(
        "room",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("building", sa.String(), nullable=False),
        sa.Column("number", sa.String(), nullable=False),
        sa.Column("seats", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_room_id"), "room", ["id"], unique=False)

def downgrade() -> None:
    op.drop_index(op.f("ix_room_id"), table_name="room")
    op.drop_table("room")
    op.drop_index(op.f("ix_subject_id"), table_name="subject")
    op.drop_table("subject")
    op.drop_index(op.f("ix_teacher_user_id"), table_name="teacher")
    op.drop_index(op.f("ix_teacher_id"), table_name="teacher")
    op.drop_table("teacher")
    op.drop_index(op.f("ix_group_id"), table_name="group")
    op.drop_table("group")
