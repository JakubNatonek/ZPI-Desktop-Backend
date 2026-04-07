from typing import cast

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_user import RaplaUser
from app.cruds.rapla.crud_rapla_users import create_rapla_user


def seed_rapla_users(db: Session) -> tuple[int, str]:
    existing = (
        db.query(RaplaUser)
        .filter(RaplaUser.username == "admin")
        .filter(RaplaUser.email == "")
        .first()
    )
    if existing:
        print("Rapla users already seeded.")
        return cast(int, existing.id), cast(str, existing.uuid)

    # create via CRUD to centralize logic
    created_user = create_rapla_user(
        db,
        username="admin",
        email="",
        password="",
        name="",
        isadmin=True,
    )

    print("Rapla users seeded.")

    return cast(int, created_user.id), cast(str, created_user.uuid)