from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.model_user import User
from app.models.model_subject import Subject
from app.models.model_subject_preference import SubjectPreference
from app.seed_data.seed_model.seed_subjects import SAMPLE_SUBJECTS
from app.models.model_activity import Activity
from app.models.model_semestr import Semestr
from app.models.model_teaching_load_assignment import TeachingLoadAssignment
from app.cruds.crud_roles_for_user import get_roles_for_user
from app.cruds.crud_subject_for_field_of_study import (
    add_subject_to_field_of_study,
    get_primary_field_of_study_for_subject,
)
from app.cruds.crud_audit import log_change
from app.cruds.crud_teaching_load import map_teaching_load_to_response
from app.models.model_subject_activity import SubjectActivity


def seed_teaching_loads(db: Session) -> None:
    """Seed teaching load assignments based on subject preferences.

    For each lecturer, a teaching load assignment is created ONLY for subjects
    that the lecturer has in their subject preferences.
    """

    # Get all lecturers (wykladowca role)
    users = db.query(User).all()
    lecturers = []
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

    semester = db.query(Semestr).first()
    if not semester:
        print("No semester found. Skipping teaching load seeding.")
        return

    # Build a mapping of subject name -> activity_ids from SAMPLE_SUBJECTS
    # to determine which activity type goes with each subject variant
    subject_activities_map: dict[str, list[int]] = {}
    for entry in SAMPLE_SUBJECTS:
        name = entry["name"]
        activity_name = entry["activity"]
        activity = (
            db.query(Activity)
            .filter(Activity.name == activity_name)
            .first()
        )
        if activity:
            subject_activities_map.setdefault(name, []).append(activity.id)

    created_count = 0

    for lecturer in lecturers:
        # Get the subjects this lecturer prefers
        preferences = (
            db.query(SubjectPreference)
            .filter(SubjectPreference.user_id == lecturer.user_id)
            .all()
        )

        if not preferences:
            print(
                f"Lecturer {lecturer.user_id} has no subject preferences — skipping teaching load."
            )
            continue

        for pref in preferences:
            subject = db.query(Subject).filter(Subject.id == pref.subject_id).first()
            if not subject:
                continue

            # Determine which activity type to use for this subject
            activity_ids = subject_activities_map.get(subject.name, [])
            activity_id: int | None = None

            # 1) Use type_link activity if available
            if (
                getattr(subject, "type_link", None)
                and getattr(subject.type_link, "activity", None)
            ):
                activity_id = subject.type_link.activity.id
            # 2) Fall back to the matching activity from the sample data
            elif activity_ids:
                activity_id = activity_ids[0]
            # 3) Last resort: try subject_activities relationship
            elif (
                getattr(subject, "subject_activities", None)
                and len(subject.subject_activities) > 0
            ):
                activity_id = subject.subject_activities[0].activity_id
            else:
                print(
                    f"Cannot determine activity for subject '{subject.name}' (id={subject.id}) — skipping."
                )
                continue

            field_of_study = get_primary_field_of_study_for_subject(db, subject.id)
            if field_of_study is None or field_of_study.id is None:
                continue

            subject_field_mapping = add_subject_to_field_of_study(
                db,
                subject_id=subject.id,
                field_of_study_id=field_of_study.id,
            )

            hours = 30  # default hours per preferred subject

            # Check if this assignment already exists
            exists = (
                db.query(TeachingLoadAssignment)
                .filter(
                    and_(
                        TeachingLoadAssignment.teacher_id == lecturer.user_id,
                        TeachingLoadAssignment.subject_id == subject.id,
                        TeachingLoadAssignment.activity_id == activity_id,
                        TeachingLoadAssignment.semester_id == semester.id,
                        TeachingLoadAssignment.subject_for_field_of_study_id
                        == subject_field_mapping.id,
                    )
                )
                .first()
            )

            if not exists:
                # Ensure subject-activity mapping exists
                sa = (
                    db.query(SubjectActivity)
                    .filter(
                        SubjectActivity.subject_id == subject.id,
                        SubjectActivity.activity_id == activity_id,
                    )
                    .first()
                )
                if sa is None:
                    sa = SubjectActivity(
                        subject_id=subject.id, activity_id=activity_id
                    )
                    db.add(sa)
                    db.flush()

                assignment = TeachingLoadAssignment(
                    teacher_id=lecturer.user_id,
                    subject_id=subject.id,
                    activity_id=activity_id,
                    semester_id=semester.id,
                    subject_for_field_of_study_id=subject_field_mapping.id,
                    hours=hours,
                )
                db.add(assignment)
                db.commit()
                created_count += 1

                # Try to add audit log entry
                try:
                    seeder_user = (
                        db.query(User).filter(User.login == "admin").first()
                    )
                    seeder_user_id = (
                        seeder_user.user_id if seeder_user is not None else None
                    )
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
                except Exception as e:
                    print(
                        f"Failed to log audit for teaching load id={assignment.id}: {e}"
                    )

    db.commit()
    print(f"Teaching loads seeded. Added: {created_count}")