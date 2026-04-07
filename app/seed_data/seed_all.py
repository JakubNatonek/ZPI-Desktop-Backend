from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.model_user import User
#from app.seed_data.rapla.seed_rapla_all import seed_rapla_all
from app.seed_data.seed_model import (
	seed_days,
	seed_dezyderata,
	seed_departments,
	seed_departments_for_user,
	seed_grades,
	seed_groups,
	seed_roles,
	seed_rooms,
	seed_room_types,
	seed_semesters,
	seed_subjects,
	seed_teacher_student_profiles,
	seed_users,
	seed_admin,
)

from app.seed_data.rapla.seed_rapla_all import seed_rapla_all


def _get_admin_id(db) -> int:
	admin = db.query(User).filter(User.login == "admin").first()
	if admin is None:
		raise RuntimeError("Missing app admin. Run base user seeders first.")

	return admin.user_id


def seed_all() -> None:
    db: Session = SessionLocal()
    try:
        # for app
        seed_departments(db)
        seed_roles(db)
        seed_room_types(db)
        admin_id: int = seed_admin(db)
        seed_users(db)
        
       
        # seed_departments_for_user(db)
        
        seed_rooms(db)
        
        seed_days(db)
        seed_semesters(db)
     

        #for rapla
        seed_rapla_all(db, admin_id)

 
        # default availability preference for a test user
        seed_dezyderata(db)
        
        # seed_grades(db)
        # seed_groups(db)
        # seed_subjects(db)
        # seed_teacher_student_profiles(db)

        print("All rapla seed data applied.")
    finally:
        db.close()

	try:




		
		#seed_rapla_all(db, _get_admin_id(db))
	finally:
		db.close()


if __name__ == "__main__":
	seed_all()