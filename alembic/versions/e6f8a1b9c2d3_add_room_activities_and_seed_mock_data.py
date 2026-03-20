"""add room activities and seed mock data

Revision ID: e6f8a1b9c2d3
Revises: d4a2f8c1b6e3
Create Date: 2026-03-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e6f8a1b9c2d3"
down_revision: Union[str, Sequence[str], None] = "d4a2f8c1b6e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "room" not in table_names:
        op.create_table(
            "room",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("building", sa.String(), nullable=False),
            sa.Column("number", sa.String(), nullable=False),
            sa.Column("seats", sa.Integer(), nullable=False),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("type", sa.String(), nullable=True),
            sa.Column("activities", sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_room_id"), "room", ["id"], unique=False)
    else:
        columns = _column_names(inspector, "room")

        if "building" not in columns:
            op.add_column("room", sa.Column("building", sa.String(), nullable=True))
        if "number" not in columns:
            op.add_column("room", sa.Column("number", sa.String(), nullable=True))
        if "seats" not in columns:
            op.add_column("room", sa.Column("seats", sa.Integer(), nullable=True))
        if "description" not in columns:
            op.add_column("room", sa.Column("description", sa.String(), nullable=True))
        if "type" not in columns:
            op.add_column("room", sa.Column("type", sa.String(), nullable=True))
        if "activities" not in columns:
            op.add_column("room", sa.Column("activities", sa.Text(), nullable=True))

        inspector = sa.inspect(bind)
        columns = _column_names(inspector, "room")

        if "budynek" in columns:
            op.execute("UPDATE room SET building = COALESCE(building, budynek)")
        if "nr" in columns:
            op.execute("UPDATE room SET number = COALESCE(number, nr)")
        if "miejsca" in columns:
            op.execute("UPDATE room SET seats = COALESCE(seats, miejsca)")
        if "opis" in columns:
            op.execute("UPDATE room SET description = COALESCE(description, opis)")
        if "typ" in columns:
            op.execute("UPDATE room SET type = COALESCE(type, typ)")

        op.execute("UPDATE room SET building = COALESCE(NULLIF(building, ''), 'A')")
        op.execute("UPDATE room SET number = COALESCE(NULLIF(number, ''), 'N/A')")
        op.execute("UPDATE room SET seats = COALESCE(seats, 1)")

    rooms_table = sa.table(
        "room",
        sa.column("building", sa.String()),
        sa.column("number", sa.String()),
        sa.column("seats", sa.Integer()),
        sa.column("description", sa.String()),
        sa.column("type", sa.String()),
        sa.column("activities", sa.Text()),
    )

    has_rooms = bind.execute(sa.text("SELECT 1 FROM room LIMIT 1")).first()
    if has_rooms is None:
        op.bulk_insert(
            rooms_table,
            [
                {
                    "building": "A",
                    "number": "A-205",
                    "seats": 30,
                    "description": "Komputery stacjonarne, projektor multimedialny",
                    "type": "informatyczna",
                    "activities": '["Programowanie", "Bazy danych", "Sieci komputerowe"]',
                },
                {
                    "building": "B",
                    "number": "B-101",
                    "seats": 120,
                    "description": "Nagłośnienie, ekran główny",
                    "type": "wykladowa",
                    "activities": '["Wyklady ogolne", "Seminaria", "Prezentacje projektow"]',
                },
                {
                    "building": "C",
                    "number": "C-12",
                    "seats": 24,
                    "description": "Stanowiska PLC, makiety automatyki",
                    "type": "mechatroniczna",
                    "activities": '["Podstawy mechatroniki", "Automatyka i robotyka"]',
                },
                {
                    "building": "D",
                    "number": "D-18",
                    "seats": 20,
                    "description": "Stanowiska pomiarowe, zasilacze laboratoryjne",
                    "type": "elektrotechniczna",
                    "activities": '["Elektrotechnika", "Pomiary elektryczne"]',
                },
                {
                    "building": "E",
                    "number": "E-07",
                    "seats": 16,
                    "description": "Stoły warsztatowe, zestawy prototypowe",
                    "type": "laboratoryjna",
                    "activities": '["Laboratoria projektowe", "Zajecia praktyczne"]',
                },
                {
                    "building": "F",
                    "number": "F-03",
                    "seats": 18,
                    "description": "Sala wielozadaniowa",
                    "type": "inna",
                    "activities": '["Zajecia specjalistyczne", "Warsztaty"]',
                },
            ],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())
    if "room" not in table_names:
        return

    columns = _column_names(inspector, "room")
    if "activities" in columns:
        op.drop_column("room", "activities")
