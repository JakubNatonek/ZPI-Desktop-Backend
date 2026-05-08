from sqlalchemy.orm import Session

from app.models.model_teaching_load import TeachingLoadAssignment
from app.models.model_user import User
from app.models.model_subject import Subject
from app.models.model_activity import Activity
from app.models.model_semestr import Semestr


def seed_teaching_loads(db: Session) -> None:
    existing = db.query(TeachingLoadAssignment).count()
    if existing > 0:
        print(f"Teaching loads already seeded ({existing} records). Skipping.")
        return

    # Resolve subjects by id (seeded with fixed ids in seed_subjects.py)
    subject_ids = {1, 2, 3, 4, 5, 6, 9, 10}
    subjects = {s.id: s for s in db.query(Subject).filter(Subject.id.in_(subject_ids)).all()}

    # Resolve activities by name
    activity_names = ["wykłady", "laboratoria", "ćwiczenia", "seminaria", "projekty"]
    activities = {a.name: a for a in db.query(Activity).filter(Activity.name.in_(activity_names)).all()}

    # Fallback: try without diacritics variants
    alt_names = ["wyklady", "laboratoria", "cwiczenia", "seminaria", "projekty"]
    for alt in alt_names:
        if alt not in activities:
            a = db.query(Activity).filter(Activity.name == alt).first()
            if a:
                activities[alt] = a

    # Resolve semesters
    semesters = {s.nazwa: s for s in db.query(Semestr).all()}
    sem_winter = semesters.get("Semestr zimowy 2025/2026")
    sem_summer = semesters.get("Semestr letni 2025/2026")

    if not sem_winter or not sem_summer:
        print("Teaching loads seed: semesters not found, skipping.")
        return

    def act(name: str) -> Activity | None:
        return activities.get(name) or activities.get(name.replace("ę", "e").replace("ó", "o").replace("ą", "a"))

    # Resolve lecturer users (any user with role lecturer / wykladowca)
    # Use first 3 non-admin users as sample lecturers
    lecturers = db.query(User).filter(User.user_id != 1).limit(4).all()
    if not lecturers:
        print("Teaching loads seed: no lecturer users found, skipping.")
        return

    def uid(idx: int) -> int:
        return lecturers[idx % len(lecturers)].user_id

    wyk = act("wykłady") or act("wyklady")
    lab = act("laboratoria")
    cwicz = act("ćwiczenia") or act("cwiczenia")
    sem_act = act("seminaria")
    proj = act("projekty")

    missing_acts = [name for name, a in [("wykłady", wyk), ("laboratoria", lab)] if a is None]
    if missing_acts:
        print(f"Teaching loads seed: activities not found: {missing_acts}. Skipping.")
        return

    sample_loads = [
        # Semestr zimowy
        {"teacher_id": uid(0), "subject": subjects.get(1), "activity": wyk,   "semester": sem_winter, "hours": 30},
        {"teacher_id": uid(0), "subject": subjects.get(2), "activity": lab,   "semester": sem_winter, "hours": 30},
        {"teacher_id": uid(1), "subject": subjects.get(3), "activity": wyk,   "semester": sem_winter, "hours": 45},
        {"teacher_id": uid(1), "subject": subjects.get(4), "activity": cwicz, "semester": sem_winter, "hours": 15},
        {"teacher_id": uid(2), "subject": subjects.get(5), "activity": wyk,   "semester": sem_winter, "hours": 30},
        {"teacher_id": uid(2), "subject": subjects.get(6), "activity": lab,   "semester": sem_winter, "hours": 30},
        {"teacher_id": uid(3), "subject": subjects.get(9), "activity": sem_act or wyk, "semester": sem_winter, "hours": 30},
        {"teacher_id": uid(3), "subject": subjects.get(10), "activity": proj or lab,   "semester": sem_winter, "hours": 30},
        # Semestr letni
        {"teacher_id": uid(0), "subject": subjects.get(3), "activity": wyk,   "semester": sem_summer, "hours": 45},
        {"teacher_id": uid(1), "subject": subjects.get(5), "activity": wyk,   "semester": sem_summer, "hours": 30},
        {"teacher_id": uid(2), "subject": subjects.get(1), "activity": wyk,   "semester": sem_summer, "hours": 30},
        {"teacher_id": uid(2), "subject": subjects.get(2), "activity": lab,   "semester": sem_summer, "hours": 30},
    ]

    created = 0
    for entry in sample_loads:
        subj = entry["subject"]
        act_obj = entry["activity"]
        if subj is None or act_obj is None:
            continue
        assignment = TeachingLoadAssignment(
            teacher_id=entry["teacher_id"],
            subject_id=subj.id,
            activity_id=act_obj.id,
            semester_id=entry["semester"].id,
            hours=entry["hours"],
        )
        db.add(assignment)
        created += 1

    db.commit()
    print(f"Teaching loads seeded: {created} records.")
