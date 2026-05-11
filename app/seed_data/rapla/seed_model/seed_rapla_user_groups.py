from typing import cast

from sqlalchemy.orm import Session

from app.cruds.rapla.crud_rapla_categories import create_rapla_category
from app.models.model_department import Department


def seed_rapla_user_groups(db: Session) -> None:
    category = create_rapla_category(
        db,
        key="user-groups",
        language_names=[("en", "user-groups")],
    )

    create_rapla_category(
        db,
        key="create-events",
        parent_id=cast(int, category.id),
        language_names=[("en", "create events")],
    )
    create_rapla_category(
        db,
        key="exchange-synchronization",
        parent_id=cast(int, category.id),
        language_names=[("en", "exchange-synchronization")],
    )
    create_rapla_category(
        db,
        key="read-events-from-others",
        parent_id=cast(int, category.id),
        language_names=[("en", "See events of other users")],
    )

    departments = db.query(Department).order_by(Department.abbreviation.asc()).all()
    for department in departments:
        abbreviation = cast(str | None, getattr(department, "abbreviation", None))
        if not abbreviation:
            continue
        if abbreviation.strip().upper() == "ADM":
            continue

        group_key = f"{abbreviation}_Editor"
        create_rapla_category(
            db,
            key=group_key,
            parent_id=cast(int, category.id),
            language_names=[("en", group_key)],
        )
