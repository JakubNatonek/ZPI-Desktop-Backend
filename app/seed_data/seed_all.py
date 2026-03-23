from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.seed_data.seed_admin import seed_admin
from app.seed_data.seed_language_name_for_category import seed_language_name_for_category
from app.seed_data.seed_departments import seed_departments
from app.seed_data.seed_language_abbreviations import seed_language_abbreviations
from app.seed_data.seed_rapla_user_to_app_user import seed_rapla_user_to_app_user
from app.seed_data.seed_rapla_users import seed_rapla_users
from app.seed_data.seed_roles import seed_roles


def seed_all() -> None:
    db: Session = SessionLocal()
    try:
        seed_departments(db)
        seed_roles(db)
        seed_rapla_users(db)
        seed_language_abbreviations(db)
        db.commit()
        seed_admin()
        seed_language_name_for_category()
        seed_rapla_user_to_app_user()
        print("All seed data applied.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
