from sqlalchemy.orm import Session

from app.models.model_user import User
from app.models.model_subject import Subject
from app.models.model_teaching_load_assignment import TeachingLoadAssignment
from app.cruds.crud_roles_for_user import get_roles_for_user
from app.cruds.crud_subject_preferences import add_preference
from fastapi import HTTPException


def seed_subject_preferences(db: Session) -> None:
    """Seed subject preferences for lecturers.

    For lecturers that have teaching load assignments, preferences are created
    for the subjects they are already assigned to teach. For lecturers without
    teaching loads, a reasonable set of subjects is assigned (the first few
    subjects from the available list) to have sample data available.
    """

    # Get all lecturers (wykladowca role)
    users = db.query(User).all()
    lecturers = []
    for user in users:
        roles = {str(role.name).strip().lower() for role in get_roles_for_user(db, user.user_id) if role.name}
        if "wykladowca" in roles or "lecturer" in roles:
            lecturers.append(user)

    if not lecturers:
        print("No lecturers found. Skipping subject preferences seeding.")
        return

    # Get available subjects
    subjects = db.query(Subject).all()

    if not subjects:
        print("No subjects found. Skipping subject preferences seeding.")
        return

    created_count = 0

    for lecturer in lecturers:
        # Check if lecturer has teaching load assignments
        assignments = (
            db.query(TeachingLoadAssignment.subject_id)
            .filter(TeachingLoadAssignment.teacher_id == lecturer.user_id)
            .distinct()
            .all()
        )
        assigned_subject_ids = {row[0] for row in assignments}

        if assigned_subject_ids:
            # Prefer subjects from teaching loads, but limit to 2-4 per lecturer
            selected_subjects = [
                s for s in subjects if s.id in assigned_subject_ids
            ][:4]
        else:
            # No teaching loads — assign first few subjects as sample preferences
            selected_subjects = subjects[:3]

        for subject in selected_subjects:
            try:
                add_preference(db, lecturer.user_id, subject.id)
                created_count += 1
            except HTTPException as e:
                if e.status_code == 400:
                    # Already exists, skip
                    pass
                else:
                    print(f"Error adding preference for lecturer {lecturer.user_id}, subject {subject.id}: {e.detail}")
            except Exception as e:
                print(f"Unexpected error adding preference for lecturer {lecturer.user_id}, subject {subject.id}: {e}")

    print(f"Subject preferences seeded. Created {created_count} preferences.")