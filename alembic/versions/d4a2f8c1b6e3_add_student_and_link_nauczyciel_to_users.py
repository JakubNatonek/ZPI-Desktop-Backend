"""add student table and link nauczyciel to users

Revision ID: d4a2f8c1b6e3
Revises: 9f1d6b2c4a77
Create Date: 2026-03-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4a2f8c1b6e3"
down_revision: Union[str, Sequence[str], None] = "0a1b2c3d4e5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "student" not in table_names:
        op.create_table(
            "student",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("nr_indeksu", sa.String(), nullable=True),
            sa.Column("group_id", sa.Integer(), nullable=True),
            sa.Column("semester", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(["group_id"], ["group.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("nr_indeksu"),
            sa.UniqueConstraint("user_id"),
        )
        op.create_index(op.f("ix_student_id"), "student", ["id"], unique=False)
        op.create_index(op.f("ix_student_user_id"), "student", ["user_id"], unique=False)
        op.create_index(op.f("ix_student_nr_indeksu"), "student", ["nr_indeksu"], unique=False)
        op.create_index(op.f("ix_student_group_id"), "student", ["group_id"], unique=False)

    if "nauczyciel" not in table_names:
        op.create_table(
            "nauczyciel",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("tytul", sa.String(), nullable=True),
            sa.Column("prop", sa.String(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id"),
        )
        op.create_index(op.f("ix_nauczyciel_id"), "nauczyciel", ["id"], unique=False)
        op.create_index(op.f("ix_nauczyciel_user_id"), "nauczyciel", ["user_id"], unique=False)
    else:
        columns = {column["name"] for column in inspector.get_columns("nauczyciel")}
        if "user_id" not in columns:
            op.add_column("nauczyciel", sa.Column("user_id", sa.Integer(), nullable=True))
            op.create_index(op.f("ix_nauczyciel_user_id"), "nauczyciel", ["user_id"], unique=False)

        inspector = sa.inspect(bind)
        foreign_keys = inspector.get_foreign_keys("nauczyciel")
        user_fk_exists = any(
            fk.get("referred_table") == "users" and "user_id" in (fk.get("constrained_columns") or [])
            for fk in foreign_keys
        )
        if not user_fk_exists:
            op.create_foreign_key(
                "fk_nauczyciel_user_id_users",
                "nauczyciel",
                "users",
                ["user_id"],
                ["user_id"],
                ondelete="CASCADE",
            )

        unique_constraints = inspector.get_unique_constraints("nauczyciel")
        unique_user_exists = any("user_id" in (uq.get("column_names") or []) for uq in unique_constraints)
        if not unique_user_exists:
            op.create_unique_constraint("uq_nauczyciel_user_id", "nauczyciel", ["user_id"])


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "student" in table_names:
        op.drop_index(op.f("ix_student_grupa_id"), table_name="student")
        op.drop_index(op.f("ix_student_nr_indeksu"), table_name="student")
        op.drop_index(op.f("ix_student_user_id"), table_name="student")
        op.drop_index(op.f("ix_student_id"), table_name="student")
        op.drop_table("student")

    if "nauczyciel" in table_names:
        op.execute("ALTER TABLE nauczyciel DROP CONSTRAINT IF EXISTS fk_nauczyciel_user_id_users;")
        op.execute("ALTER TABLE nauczyciel DROP CONSTRAINT IF EXISTS uq_nauczyciel_user_id;")
        op.execute("ALTER TABLE nauczyciel DROP CONSTRAINT IF EXISTS nauczyciel_user_id_key;")
        op.execute("DROP INDEX IF EXISTS ix_nauczyciel_user_id;")
        op.execute("ALTER TABLE nauczyciel DROP COLUMN IF EXISTS user_id;")
