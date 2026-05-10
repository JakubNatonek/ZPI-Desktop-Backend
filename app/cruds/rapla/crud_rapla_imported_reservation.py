"""CRUD for rapla_imported_reservations with diff-based audit logging.

Flow:
  1. parse_rapla_reservations(xml_text)  →  list[ParsedReservation]
  2. upsert_rapla_reservations(db, parsed_list, modified_by, modified_by_name)
     - For each parsed reservation:
         * If UUID not in DB  →  INSERT + create_audit_log(action="create")
         * If UUID exists and any field changed  →  UPDATE + create_audit_log(action="update")
         * UUIDs present in DB but missing from file  →  no deletion (non-destructive import)
     - Returns a summary dict
"""
from __future__ import annotations

import json
from typing import Optional

from sqlalchemy.orm import Session

from app.cruds.crud_audit_logs import create_audit_log
from app.models.rapla.model_rapla_imported_reservation import RaplaImportedReservation
from app.services.rapla_xml_parser import ParsedReservation

_ENTITY = "rapla_reservation"

_TRACKED_FIELDS = (
    "name",
    "color",
    "start_date",
    "start_time",
    "end_date",
    "end_time",
    "repeating_type",
    "repeating_end_date",
    "allocate",
    "room_names",
    "teacher_names",
    "semester_names",
)


def _row_to_dict(row: RaplaImportedReservation) -> dict:
    return {
        "name": row.name,
        "color": row.color,
        "start_date": row.start_date,
        "start_time": row.start_time,
        "end_date": row.end_date,
        "end_time": row.end_time,
        "repeating_type": row.repeating_type,
        "repeating_end_date": row.repeating_end_date,
        "allocate": row.allocate or [],
        "room_names": row.room_names or [],
        "teacher_names": row.teacher_names or [],
        "semester_names": row.semester_names or [],
    }


def _has_changed(old: dict, new: dict) -> bool:
    """Deep comparison via JSON serialisation (handles list equality)."""
    return json.dumps(old, sort_keys=True) != json.dumps(new, sort_keys=True)


def get_by_uuid(db: Session, uuid: str) -> Optional[RaplaImportedReservation]:
    return (
        db.query(RaplaImportedReservation)
        .filter(RaplaImportedReservation.uuid == uuid)
        .first()
    )


def upsert_rapla_reservations(
    db: Session,
    reservations: list[ParsedReservation],
    modified_by: int,
    modified_by_name: str,
) -> dict:
    """Insert or update Rapla reservations and emit audit log entries for changes.

    Returns a summary dict: {created: int, updated: int, unchanged: int}
    """
    created = 0
    updated = 0
    unchanged = 0
    deleted = 0

    # Keep DB synchronized with the latest imported file content.
    # Remove reservations that are not present in the current XML payload.
    incoming_uuids = {item.uuid for item in reservations}
    stale_rows = (
        db.query(RaplaImportedReservation)
        .filter(~RaplaImportedReservation.uuid.in_(incoming_uuids))
        .all()
    )
    for stale in stale_rows:
        old_values = _row_to_dict(stale)
        db.delete(stale)
        create_audit_log(
            db=db,
            entity_name=_ENTITY,
            entity_id=stale.id,
            action="delete",
            modified_by=modified_by,
            modified_by_name=modified_by_name,
            old_values=old_values,
            new_values=None,
        )
        deleted += 1

    for parsed in reservations:
        new_values = parsed.to_dict()
        existing = get_by_uuid(db, parsed.uuid)

        if existing is None:
            # New reservation — INSERT
            row = RaplaImportedReservation(
                uuid=parsed.uuid,
                name=parsed.name,
                color=parsed.color,
                start_date=parsed.start_date,
                start_time=parsed.start_time,
                end_date=parsed.end_date,
                end_time=parsed.end_time,
                repeating_type=parsed.repeating_type,
                repeating_end_date=parsed.repeating_end_date,
                allocate=parsed.allocate,
                room_names=parsed.room_names,
                teacher_names=parsed.teacher_names,
                semester_names=parsed.semester_names,
            )
            db.add(row)
            db.flush()  # get the generated id

            create_audit_log(
                db=db,
                entity_name=_ENTITY,
                entity_id=row.id,
                action="create",
                modified_by=modified_by,
                modified_by_name=modified_by_name,
                old_values=None,
                new_values=new_values,
            )
            created += 1

        else:
            old_values = _row_to_dict(existing)

            if _has_changed(old_values, new_values):
                # Update stored row
                existing.name = parsed.name
                existing.color = parsed.color
                existing.start_date = parsed.start_date
                existing.start_time = parsed.start_time
                existing.end_date = parsed.end_date
                existing.end_time = parsed.end_time
                existing.repeating_type = parsed.repeating_type
                existing.repeating_end_date = parsed.repeating_end_date
                existing.allocate = parsed.allocate
                existing.room_names = parsed.room_names
                existing.teacher_names = parsed.teacher_names
                existing.semester_names = parsed.semester_names
                db.flush()

                create_audit_log(
                    db=db,
                    entity_name=_ENTITY,
                    entity_id=existing.id,
                    action="update",
                    modified_by=modified_by,
                    modified_by_name=modified_by_name,
                    old_values=old_values,
                    new_values=new_values,
                )
                updated += 1
            else:
                unchanged += 1

    db.commit()
    return {"created": created, "updated": updated, "unchanged": unchanged, "deleted": deleted}
