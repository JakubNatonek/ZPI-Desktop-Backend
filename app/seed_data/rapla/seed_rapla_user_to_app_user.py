from sqlalchemy.orm import Session

from app.models.model_user import User
from app.models.rapla.model_rapla_user import RaplaUser
from app.models.rapla.model_rapla_user_to_app_user import RaplaUserToAppUser
from app.cruds.rapla.crud_rapla_user_to_app_user import create_rapla_user_mapping


def seed_rapla_user_to_app_user(db: Session, admin_id: int, rapla_admin_id: int) -> None:

    app_admin = db.query(User).filter(User.user_id == admin_id).first()
    rapla_admin = db.query(RaplaUser).filter(RaplaUser.id == rapla_admin_id).first()

    if app_admin is None:
        raise RuntimeError("Missing app admin. Run app user seeders first.")
    if rapla_admin is None:
        raise RuntimeError("Missing Rapla admin. Run Rapla user seeders first.")

    existing = (
        db.query(RaplaUserToAppUser)
        .filter(RaplaUserToAppUser.app_user_id == admin_id)
        .filter(RaplaUserToAppUser.rapla_user_id == rapla_admin_id)
        .first()
    )
    if existing:
        print("Rapla-to-app user mapping already seeded.")
        return

    create_rapla_user_mapping(db, admin_id, rapla_admin_id)
    print("Rapla-to-app user mapping seeded.")
