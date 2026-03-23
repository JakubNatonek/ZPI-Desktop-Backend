from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.rapla.model_rapla_user import RaplaUser


def seed_rapla_users(db: Session | None = None) -> None:
    own_session = db is None
    if db is None:
        db = SessionLocal()

    try:
        existing = (
            db.query(RaplaUser)
            .filter(RaplaUser.username == "admin")
            .filter(RaplaUser.email == "")
            .first()
        )
        if existing:
            if own_session:
                print("Rapla users already seeded.")
            return

        now = datetime.now(timezone.utc)

        db.add(
            RaplaUser(
                uuid=str(uuid4()),
                created_at=now,
                last_changed=now,
                username="admin",
                password="",
                name="",
                email="",
                isadmin=True,
            )
        )

        if own_session:
            db.commit()
            print("Rapla users seeded.")
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    seed_rapla_users()
