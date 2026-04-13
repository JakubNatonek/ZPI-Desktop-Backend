"""add subject activities table and migrate subject.type to type_id

Revision ID: 20260413_0001
Revises:
Create Date: 2026-04-13 00:01:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "20260413_0001"
down_revision = None
branch_labels = None
depends_on = None


def _has_table(bind, table_name: str) -> bool:
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def _has_column(bind, table_name: str, column_name: str) -> bool:
    inspector = inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def _has_index(bind, table_name: str, index_name: str) -> bool:
    inspector = inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def _has_fk(bind, table_name: str, fk_name: str) -> bool:
    inspector = inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(fk["name"] == fk_name for fk in inspector.get_foreign_keys(table_name))


def upgrade() -> None:
    bind = op.get_bind()

    if not _has_table(bind, "subject_activities"):
        op.create_table(
            "subject_activities",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("subject_id", sa.Integer(), nullable=False),
            sa.Column("activity_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["subject_id"], ["subject.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["activity_id"], ["activities.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("subject_id", "activity_id", name="uq_subject_activities_subject_activity"),
        )

    if not _has_index(bind, "subject_activities", "ix_subject_activities_subject_id"):
        op.create_index("ix_subject_activities_subject_id", "subject_activities", ["subject_id"], unique=False)

    if not _has_index(bind, "subject_activities", "ix_subject_activities_activity_id"):
        op.create_index("ix_subject_activities_activity_id", "subject_activities", ["activity_id"], unique=False)

    if _has_table(bind, "subject") and not _has_column(bind, "subject", "type_id"):
        op.add_column("subject", sa.Column("type_id", sa.Integer(), nullable=True))

    if _has_table(bind, "subject") and not _has_index(bind, "subject", "ix_subject_type_id"):
        op.create_index("ix_subject_type_id", "subject", ["type_id"], unique=False)

    if _has_table(bind, "subject") and not _has_fk(bind, "subject", "fk_subject_type_id_subject_activities"):
        op.create_foreign_key(
            "fk_subject_type_id_subject_activities",
            "subject",
            "subject_activities",
            ["type_id"],
            ["id"],
        )

    if _has_table(bind, "subject") and _has_column(bind, "subject", "type"):
        rows = bind.execute(sa.text("SELECT id, type FROM subject")).mappings().all()

        for row in rows:
            subject_id = int(row["id"])
            type_value = str(row["type"] or "").strip()
            activity_name = type_value or "nieokreslone"

            activity_row = bind.execute(
                sa.text("SELECT id FROM activities WHERE lower(name) = lower(:name) LIMIT 1"),
                {"name": activity_name},
            ).mappings().first()

            if activity_row is None:
                activity_row = bind.execute(
                    sa.text("INSERT INTO activities (name) VALUES (:name) RETURNING id"),
                    {"name": activity_name},
                ).mappings().first()

            activity_id = int(activity_row["id"])

            link_row = bind.execute(
                sa.text(
                    "SELECT id FROM subject_activities "
                    "WHERE subject_id = :subject_id AND activity_id = :activity_id LIMIT 1"
                ),
                {"subject_id": subject_id, "activity_id": activity_id},
            ).mappings().first()

            if link_row is None:
                link_row = bind.execute(
                    sa.text(
                        "INSERT INTO subject_activities (subject_id, activity_id) "
                        "VALUES (:subject_id, :activity_id) RETURNING id"
                    ),
                    {"subject_id": subject_id, "activity_id": activity_id},
                ).mappings().first()

            type_id = int(link_row["id"])
            bind.execute(
                sa.text("UPDATE subject SET type_id = :type_id WHERE id = :subject_id"),
                {"type_id": type_id, "subject_id": subject_id},
            )

        with op.batch_alter_table("subject") as batch_op:
            batch_op.drop_column("type")


def downgrade() -> None:
    bind = op.get_bind()

    if _has_table(bind, "subject") and not _has_column(bind, "subject", "type"):
        op.add_column("subject", sa.Column("type", sa.String(), nullable=True))

    if _has_table(bind, "subject") and _has_column(bind, "subject", "type"):
        bind.execute(
            sa.text(
                """
                UPDATE subject AS s
                SET type = COALESCE(a.name, 'nieokreslone')
                FROM subject_activities AS sa
                LEFT JOIN activities AS a ON a.id = sa.activity_id
                WHERE s.type_id = sa.id
                """
            )
        )
        bind.execute(sa.text("UPDATE subject SET type = 'nieokreslone' WHERE type IS NULL OR btrim(type) = ''"))

    if _has_table(bind, "subject") and _has_fk(bind, "subject", "fk_subject_type_id_subject_activities"):
        op.drop_constraint("fk_subject_type_id_subject_activities", "subject", type_="foreignkey")

    if _has_table(bind, "subject") and _has_index(bind, "subject", "ix_subject_type_id"):
        op.drop_index("ix_subject_type_id", table_name="subject")

    if _has_table(bind, "subject") and _has_column(bind, "subject", "type_id"):
        with op.batch_alter_table("subject") as batch_op:
            batch_op.drop_column("type_id")

    if _has_table(bind, "subject_activities") and _has_index(bind, "subject_activities", "ix_subject_activities_activity_id"):
        op.drop_index("ix_subject_activities_activity_id", table_name="subject_activities")

    if _has_table(bind, "subject_activities") and _has_index(bind, "subject_activities", "ix_subject_activities_subject_id"):
        op.drop_index("ix_subject_activities_subject_id", table_name="subject_activities")

    if _has_table(bind, "subject_activities"):
        op.drop_table("subject_activities")
