from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.model_user import User
from app.models.rapla.model_rapla_user import RaplaUser
from app.models.rapla.model_rapla_user_to_app_user import RaplaUserToAppUser


def seed_rapla_user_to_app_user(db: Session | None = None) -> None:
    own_session = db is None
    if db is None:
        db = SessionLocal()

    try:
        app_admin = db.query(User).filter(User.email == "admin@admin.com").first()
        rapla_admin = db.query(RaplaUser).filter(RaplaUser.uuid == "ue1025a8-c923-425e-bb21-6fddb8889c21").first()

        if app_admin is None or rapla_admin is None:
            raise RuntimeError("Missing app admin or Rapla admin. Run user seeders first.")

        existing = (
            db.query(RaplaUserToAppUser)
            .filter(RaplaUserToAppUser.app_user_id == app_admin.user_id)
            .first()
        )
        if existing:
            if own_session:
                print("Rapla-to-app user mapping already seeded.")
            return

        db.add(
            RaplaUserToAppUser(
                app_user_id=app_admin.user_id,
                rapla_user_id=rapla_admin.id,
            )
        )

        if own_session:
            db.commit()
            print("Rapla-to-app user mapping seeded.")
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    seed_rapla_user_to_app_user()
