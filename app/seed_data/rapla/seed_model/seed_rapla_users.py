from typing import cast

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_user import RaplaUser
from app.cruds.rapla.crud_rapla_users import create_rapla_user


def seed_rapla_users(db: Session) -> tuple[int, str]:
    # Ensure Rapla admin exists (return its id/uuid for compatibility)
    admin = db.query(RaplaUser).filter(RaplaUser.username == "admin").first()
    if admin is None:
        admin = create_rapla_user(
            db,
            username="admin",
            email="",
            password="",
            name="",
            isadmin=True,
        )
        print("Created Rapla admin user.")
    else:
        print("Rapla admin user already exists.")

    # Ensure a "system" Rapla user exists. Use a unique non-empty email to avoid
    # colliding with the admin's empty email value.
    system = db.query(RaplaUser).filter(RaplaUser.username == "system").first()
    if system is None:
        try:
            system = create_rapla_user(
                db,
                username="system",
                email="system@system.local",
                password="",
                name="System",
                isadmin=True,
            )
            print("Created Rapla system user.")
        except Exception as e:
            print(f"Failed to create Rapla system user: {e}")
    else:
        print("Rapla system user already exists.")

    return cast(int, admin.id), cast(str, admin.uuid)