from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.cruds.crud_audit import log_change
from app.cruds.crud_roles_for_user import get_roles_for_user
from app.cruds.crud_subject_for_field_of_study import (
    add_subject_to_field_of_study,
    get_primary_field_of_study_for_subject,
)
from app.cruds.crud_teaching_load import map_teaching_load_to_response
from app.models.model_activity import Activity
from app.models.model_semestr import Semestr
from app.models.model_subject import Subject
from app.models.model_subject_activity import SubjectActivity
from app.models.model_teaching_load_assignment import TeachingLoadAssignment
from app.models.model_user import User
from app.seed_data.seed_model.seed_subjects import SAMPLE_SUBJECTS


def seed_teaching_loads(db: Session) -> None:
    """Seed teaching load assignments with sample data."""

    # Get all lecturers (wykladowca role)
    users = db.query(User).all()
    lecturers: list[User] = []
    for user in users:
        roles = {
            str(role.name).strip().lower()
            for role in get_roles_for_user(db, user.user_id)
            if role.name
        }
        if "wykladowca" in roles or "lecturer" in roles:
            lecturers.append(user)

    if not lecturers:
        print("No lecturers found. Skipping teaching load seeding.")
        return

    # Get sample data
    # Only consider subjects that were created by seed_subjects (match by name)
    seeded_subject_names = {entry["name"] for entry in SAMPLE_SUBJECTS}
    subjects = db.query(Subject).filter(Subject.name.in_(list(seeded_subject_names))).all()
    activities = db.query(Activity).all()
    semester = db.query(Semestr).first()

    if not subjects or not activities or not semester:
        print("Missing required data (subjects, activities, or semester). Skipping teaching load seeding.")
        return

    # Create sample assignments
    sample_assignments: list[dict[str, int]] = []
    for idx, lecturer in enumerate(lecturers[:3]):
        for subject_idx, subject in enumerate(subjects):
            # Pick activity linked to the subject: prefer primary type_link, else first subject_activity
            activity_id = None
            if getattr(subject, "type_link", None) and getattr(subject.type_link, "activity", None):
                activity_id = subject.type_link.activity.id
            elif getattr(subject, "subject_activities", None) and len(subject.subject_activities) > 0:
                activity_id = subject.subject_activities[0].activity_id
            else:
                # No linked activity for this subject - skip
                continue

            field_of_study = get_primary_field_of_study_for_subject(db, subject.id)
            if field_of_study is None or field_of_study.id is None:
                continue

            subject_field_mapping = add_subject_to_field_of_study(
                db,
                subject_id=subject.id,
                field_of_study_id=field_of_study.id,
            )
            hours = 15 + (idx * 5) + (subject_idx * 10)

            sample_assignments.append({
                "teacher_id": lecturer.user_id,
                "subject_id": subject.id,
                "activity_id": activity_id,
                "semester_id": semester.id,
                "subject_for_field_of_study_id": subject_field_mapping.id,
                "hours": hours,
            })

    created_count = 0

    # Try to find admin/seeder user to attribute audit entries to
    seeder_user = db.query(User).filter(User.login == "admin").first()
    seeder_user_id = seeder_user.user_id if seeder_user is not None else None

    for assignment_data in sample_assignments:
        exists = db.query(TeachingLoadAssignment).filter(
            and_(
                TeachingLoadAssignment.teacher_id == assignment_data["teacher_id"],
                TeachingLoadAssignment.subject_id == assignment_data["subject_id"],
                TeachingLoadAssignment.activity_id == assignment_data["activity_id"],
                TeachingLoadAssignment.semester_id == assignment_data["semester_id"],
                TeachingLoadAssignment.subject_for_field_of_study_id == assignment_data["subject_for_field_of_study_id"],
            )
        ).first()

        if exists is not None:
            continue

        # Ensure subject-activity mapping exists
        sa = db.query(SubjectActivity).filter(
            SubjectActivity.subject_id == assignment_data["subject_id"],
            SubjectActivity.activity_id == assignment_data["activity_id"],
        ).first()
        if sa is None:
            sa = SubjectActivity(
                subject_id=assignment_data["subject_id"],
                activity_id=assignment_data["activity_id"],
            )
            db.add(sa)
            db.flush()

        assignment = TeachingLoadAssignment(**assignment_data)
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        created_count += 1

        # Create audit log entry indicating creation by seeder/admin
        try:
            new_values = map_teaching_load_to_response(assignment)
            log_change(
                db=db,
                entity_name="TeachingLoadAssignment",
                entity_id=assignment.id,
                action="CREATE",
                old_values=None,
                new_values=new_values,
                user_id=seeder_user_id,
            )
        except Exception as exc:
            print(f"Failed to log audit for teaching load id={assignment.id}: {exc}")

    db.commit()
    print(f"Teaching loads seeded. Added: {created_count}")
