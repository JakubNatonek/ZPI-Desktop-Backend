from sqlalchemy.orm import Session

from app.seed_data.rapla.seed_rapla_language_abbreviations import seed_language_abbreviations
from app.seed_data.rapla.seed_rapla_user_to_app_user import seed_rapla_user_to_app_user
from app.seed_data.rapla.seed_rapla_users import seed_rapla_users
from app.seed_data.rapla.seed_rapla_user_groups import seed_rapla_user_groups
from app.seed_data.rapla.seed_rapla_departments import seed_rapla_departments
from app.seed_data.rapla.seed_rapla_titles import seed_rapla_titles
from app.seed_data.rapla.seed_define_nauczyciel_from_example import seed_define_nauczyciel


def seed_rapla_all(db: Session, admin_id: int) -> None:
    # for rapla
    rapla_admin_id, rapla_admin_uuid = seed_rapla_users(db)
    seed_rapla_user_to_app_user(db, admin_id, rapla_admin_id)

    seed_language_abbreviations(db)
    seed_rapla_user_groups(db)
    seed_rapla_departments(db)
    seed_rapla_titles(db)
    seed_define_nauczyciel(db, rapla_admin_uuid)

    print("All seed data applied.")