from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.seed_data import seed_model


from app.seed_data.rapla.seed_rapla_all import seed_rapla_all


def seed_all() -> None:
    db: Session = SessionLocal()
    try:
        # User
        seed_model.seed_departments(db)
        seed_model.seed_roles(db)
        seed_model.seed_titles(db)
        admin_id: int = seed_model.seed_admin(db)
        seed_model.seed_users(db)


        seed_model.seed_room_types(db)
        seed_model.seed_rooms(db)

        seed_model.seed_days(db)
        seed_model.seed_semesters(db)

        # default availability preference for a test user
        seed_model.seed_dezyderata(db)

        #for rapla
        seed_rapla_all(db = db, admin_id = admin_id)


        # NOTE: WTF is this dogshit
        # seed_departments_for_user(db)
        # seed_grades(db)
        # seed_groups(db)
        # seed_subjects(db)
        # seed_teacher_student_profiles(db)

        print("All rapla seed data applied.")
    finally:
        db.close()

if __name__ == "__main__":
	seed_all()