from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.model_audit_log import AuditLog


SAMPLE_AUDIT_LOGS = [
    {
        "entity_name": "Subject",
        "entity_id": 1,
        "action": "update",
        "old_values": {"name": "Programowanie obiektowe (stara)"},
        "new_values": {"name": "Programowanie obiektowe"},
        "modified_by": 1,
        "modified_by_name": "Admin Admin",
        "timestamp": datetime(2026, 4, 10, 9, 0, 0, tzinfo=timezone.utc),
    },
    {
        "entity_name": "Room",
        "entity_id": 2,
        "action": "update",
        "old_values": {"capacity": 20},
        "new_values": {"capacity": 30},
        "modified_by": 1,
        "modified_by_name": "Admin Admin",
        "timestamp": datetime(2026, 4, 12, 11, 30, 0, tzinfo=timezone.utc),
    },
    {
        "entity_name": "TeachingLoadAssignment",
        "entity_id": 1,
        "action": "create",
        "old_values": None,
        "new_values": {"teacher_id": 2, "subject_id": 1, "activity_id": 1, "semester_id": 1, "hours": 30},
        "modified_by": 1,
        "modified_by_name": "Admin Admin",
        "timestamp": datetime(2026, 4, 15, 8, 0, 0, tzinfo=timezone.utc),
    },
    {
        "entity_name": "TeachingLoadAssignment",
        "entity_id": 2,
        "action": "create",
        "old_values": None,
        "new_values": {"teacher_id": 3, "subject_id": 3, "activity_id": 1, "semester_id": 1, "hours": 45},
        "modified_by": 1,
        "modified_by_name": "Admin Admin",
        "timestamp": datetime(2026, 4, 15, 8, 5, 0, tzinfo=timezone.utc),
    },
    {
        "entity_name": "TeachingLoadAssignment",
        "entity_id": 1,
        "action": "update",
        "old_values": {"hours": 30},
        "new_values": {"hours": 45},
        "modified_by": 1,
        "modified_by_name": "Admin Admin",
        "timestamp": datetime(2026, 4, 20, 14, 0, 0, tzinfo=timezone.utc),
    },
    {
        "entity_name": "UnavailabilityNote",
        "entity_id": 1,
        "action": "update",
        "old_values": {"status": "pending"},
        "new_values": {"status": "accepted"},
        "modified_by": 1,
        "modified_by_name": "Admin Admin",
        "timestamp": datetime(2026, 5, 2, 10, 0, 0, tzinfo=timezone.utc),
    },
    {
        "entity_name": "User",
        "entity_id": 2,
        "action": "update",
        "old_values": {"role": "lecturer"},
        "new_values": {"role": "lecturer"},
        "modified_by": 1,
        "modified_by_name": "Admin Admin",
        "timestamp": datetime(2026, 5, 5, 16, 0, 0, tzinfo=timezone.utc),
    },
    {
        "entity_name": "TeachingLoadAssignment",
        "entity_id": 3,
        "action": "create",
        "old_values": None,
        "new_values": {"teacher_id": 2, "subject_id": 5, "activity_id": 1, "semester_id": 2, "hours": 30},
        "modified_by": 1,
        "modified_by_name": "Admin Admin",
        "timestamp": datetime(2026, 5, 7, 9, 0, 0, tzinfo=timezone.utc),
    },
]


def seed_audit_logs(db: Session) -> None:
    existing = db.query(AuditLog).count()
    if existing > 0:
        print(f"Audit logs already seeded ({existing} records). Skipping.")
        return

    for entry in SAMPLE_AUDIT_LOGS:
        log = AuditLog(**entry)
        db.add(log)

    db.commit()
    print(f"Audit logs seeded: {len(SAMPLE_AUDIT_LOGS)} records.")
