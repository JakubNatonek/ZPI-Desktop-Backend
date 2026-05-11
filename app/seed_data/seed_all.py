from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.seed_data import seed_model
from app.seed_data.seed_model.seed_field_of_study import seed_field_of_study


from app.seed_data.rapla.seed_rapla_all import seed_rapla_all


def seed_all() -> None:
    db: Session = SessionLocal()
    try:
        # User
        seed_model.seed_departments(db)
        seed_model.seed_roles(db)
        seed_model.seed_titles(db)
        admin_id: int = seed_model.seed_admin(db)
        #for rapla
        seed_rapla_all(db = db, admin_id = admin_id)
        seed_model.seed_announcements(db, author_id=admin_id)
        seed_model.seed_users(db)

        seed_model.seed_activities(db)
        seed_model.seed_special_equipment(db)


        seed_model.seed_room_types(db)
        seed_model.seed_rooms(db)

        seed_model.seed_days(db)
        seed_model.seed_semesters(db)
        seed_model.seed_thesis_settings(db)
        seed_model.seed_thesis_proposals(db)

        seed_model.seed_subjects(db)
        seed_field_of_study(db)
        seed_model.seed_groups(db)

        seed_model.seed_lessons(db)

        # Subject preferences for lecturers
        seed_model.seed_subject_preferences(db)

        # default availability preference for a test user
        seed_model.seed_dezyderata(db)

        # sample unavailability notes
        seed_model.seed_unavailability_notes(db)

        # teaching load assignments
        seed_model.seed_teaching_loads(db)

        # audit log history
        seed_model.seed_audit_logs(db)

        
        seed_model.seed_teaching_loads(db)

        # NOTE: WTF is this dogshit
        # seed_departments_for_user(db)
        # seed_grades(db)
        # seed_subjects(db)
        # seed_teacher_student_profiles(db)

        print("All rapla seed data applied.")
    finally:
        db.close()

if __name__ == "__main__":
	seed_all()