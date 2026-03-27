"""refactor_dezyderata_to_day_ranges

Revision ID: 9b2d7e8f1a2c
Revises: 4a8b7c9d0e1f
Create Date: 2026-03-27 13:30:00.000000

"""

from datetime import date, timedelta
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b2d7e8f1a2c"
down_revision: Union[str, Sequence[str], None] = "4a8b7c9d0e1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TOTAL_WEEK_HOURS = 14 * 7


def _compress_hours(hours: list[int]) -> list[tuple[int, int]]:
    if not hours:
        return []

    ranges: list[tuple[int, int]] = []
    start = hours[0]
    end = hours[0]

    for hour in hours[1:]:
        if hour == end + 1:
            end = hour
            continue

        ranges.append((start, end))
        start = hour
        end = hour

    ranges.append((start, end))
    return ranges


def _migrate_legacy_rows_to_ranges() -> None:
    conn = op.get_bind()

    day_map = {
        row.name: row.id
        for row in conn.execute(sa.text("SELECT id, name FROM days")).mappings().all()
    }

    legacy_rows = conn.execute(
        sa.text(
            """
            SELECT id, user_id, data_od, data_do, godziny, semestr_id
            FROM availability_preferences
            """
        )
    ).mappings().all()

    for row in legacy_rows:
        raw_slots = row["godziny"] or ""
        slots = [slot.strip() for slot in raw_slots.split(",") if slot.strip()]
        is_available = len(slots) <= TOTAL_WEEK_HOURS // 2

        hours_by_day_name: dict[str, set[int]] = {}

        for slot in slots:
            try:
                date_part, hour_part = slot.rsplit("-", 1)
                slot_date = date.fromisoformat(date_part)
                slot_hour = int(hour_part)
            except (TypeError, ValueError):
                continue

            if slot_hour < 0 or slot_hour > 23:
                continue

            day_name = slot_date.strftime("%A").lower()
            if day_name not in day_map:
                continue

            if day_name not in hours_by_day_name:
                hours_by_day_name[day_name] = set()
            hours_by_day_name[day_name].add(slot_hour)

        for day_name, hours in hours_by_day_name.items():
            day_id = day_map[day_name]
            sorted_hours = sorted(hours)

            for from_hour, to_hour in _compress_hours(sorted_hours):
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO availability_preferences (
                            user_id, data_od, data_do, semestr_id,
                            day_id, from_hour, to_hour, is_available
                        ) VALUES (
                            :user_id, :data_od, :data_do, :semestr_id,
                            :day_id, :from_hour, :to_hour, :is_available
                        )
                        """
                    ),
                    {
                        "user_id": row["user_id"],
                        "data_od": row["data_od"],
                        "data_do": row["data_do"],
                        "semestr_id": row["semestr_id"],
                        "day_id": day_id,
                        "from_hour": from_hour,
                        "to_hour": to_hour,
                        "is_available": is_available,
                    },
                )

        conn.execute(
            sa.text("DELETE FROM availability_preferences WHERE id = :id"),
            {"id": row["id"]},
        )


def _rebuild_legacy_hour_rows() -> None:
    conn = op.get_bind()

    rows = conn.execute(
        sa.text(
            """
            SELECT user_id, data_od, data_do, semestr_id, day_id, from_hour, to_hour
            FROM dezyderaty
            ORDER BY user_id, data_od, data_do, semestr_id, day_id, from_hour
            """
        )
    ).mappings().all()

    weekly_slots: dict[tuple[int, date, date, int], set[tuple[date, int]]] = {}

    for row in rows:
        key = (row["user_id"], row["data_od"], row["data_do"], row["semestr_id"])
        monday = row["data_od"]
        day_offset = int(row["day_id"]) - 1
        slot_date = monday + timedelta(days=day_offset)

        if key not in weekly_slots:
            weekly_slots[key] = set()

        for hour in range(int(row["from_hour"]), int(row["to_hour"]) + 1):
            weekly_slots[key].add((slot_date, hour))

    conn.execute(sa.text("DELETE FROM dezyderaty"))

    for (user_id, data_od, data_do, semestr_id), slots in weekly_slots.items():
        ordered_slots = sorted(slots, key=lambda item: (item[0], item[1]))
        godziny = ",".join(f"{slot_date.isoformat()}-{hour}" for slot_date, hour in ordered_slots)

        conn.execute(
            sa.text(
                """
                INSERT INTO dezyderaty (user_id, data_od, data_do, godziny, semestr_id)
                VALUES (:user_id, :data_od, :data_do, :godziny, :semestr_id)
                """
            ),
            {
                "user_id": user_id,
                "data_od": data_od,
                "data_do": data_do,
                "godziny": godziny,
                "semestr_id": semestr_id,
            },
        )


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table("semestr", "semesters")
    op.rename_table("dezyderaty", "availability_preferences")

    op.create_table(
        "days",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=16), nullable=False, unique=True),
    )

    op.execute(
        """
        INSERT INTO days (id, name) VALUES
        (1, 'monday'),
        (2, 'tuesday'),
        (3, 'wednesday'),
        (4, 'thursday'),
        (5, 'friday'),
        (6, 'saturday'),
        (7, 'sunday')
        """
    )

    op.add_column("availability_preferences", sa.Column("day_id", sa.Integer(), nullable=True))
    op.add_column("availability_preferences", sa.Column("from_hour", sa.Integer(), nullable=True))
    op.add_column("availability_preferences", sa.Column("to_hour", sa.Integer(), nullable=True))
    op.add_column(
        "availability_preferences",
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    op.create_foreign_key(
        "fk_availability_preferences_day_id_days",
        "availability_preferences",
        "days",
        ["day_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    _migrate_legacy_rows_to_ranges()

    op.drop_column("availability_preferences", "godziny")

    op.alter_column("availability_preferences", "day_id", nullable=False)
    op.alter_column("availability_preferences", "from_hour", nullable=False)
    op.alter_column("availability_preferences", "to_hour", nullable=False)

    op.create_check_constraint(
        "ck_availability_preferences_hour_bounds",
        "availability_preferences",
        "from_hour >= 0 AND from_hour <= 23 AND to_hour >= 0 AND to_hour <= 23 AND from_hour <= to_hour",
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table("availability_preferences", "dezyderaty")

    op.add_column("dezyderaty", sa.Column("godziny", sa.Text(), nullable=True))

    _rebuild_legacy_hour_rows()

    op.drop_constraint("ck_availability_preferences_hour_bounds", "dezyderaty", type_="check")
    op.drop_constraint("fk_availability_preferences_day_id_days", "dezyderaty", type_="foreignkey")
    op.drop_column("dezyderaty", "is_available")
    op.drop_column("dezyderaty", "to_hour")
    op.drop_column("dezyderaty", "from_hour")
    op.drop_column("dezyderaty", "day_id")

    op.alter_column("dezyderaty", "godziny", nullable=False)

    op.drop_table("days")

    op.rename_table("semesters", "semestr")
