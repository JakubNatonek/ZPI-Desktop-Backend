from datetime import datetime

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.rapla.model_rapla_user import RaplaUser


def _parse_rapla_datetime(value: str) -> datetime:
    # Rapla timestamps come in UTC with trailing Z.
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def seed_rapla_users(db: Session | None = None) -> None:
    own_session = db is None
    if db is None:
        db = SessionLocal()

    try:
        rapla_uuid = "ue1025a8-c923-425e-bb21-6fddb8889c21"
        existing = db.query(RaplaUser).filter(RaplaUser.uuid == rapla_uuid).first()
        if existing:
            if own_session:
                print("Rapla users already seeded.")
            return

        db.add(
            RaplaUser(
                uuid=rapla_uuid,
                created_at=_parse_rapla_datetime("2026-03-22T21:14:03.768Z"),
                last_changed=_parse_rapla_datetime("2026-03-22T21:14:03.768Z"),
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
