from sqlalchemy.orm import Session

from typing import cast

from app.models.rapla.model_rapla_category import RaplaCategory
from app.cruds.rapla.crud_rapla_categories import create_rapla_category
from app.cruds.rapla.crud_rapla_language_abbreviations import get_language_abbreviation_by_language
from app.cruds.rapla.crud_rapla_language_name import create_language_name
from app.cruds.rapla.crud_rapla_language_name_for_category import add_language_name_to_category


def seed_rapla_user_groups(db: Session) -> None:
    category = _seed_rapla_user_groups(db, "user-groups", "user-groups")
    _seed_rapla_user_groups(db, "create-events", "create events", cast( int, category.id ) )
    _seed_rapla_user_groups(db, "exchange-synchronization", "exchange-synchronization", cast( int, category.id ) )
    _seed_rapla_user_groups(db, "read-events-from-others", "See events of other users", cast( int, category.id ) )


def _seed_rapla_user_groups(db: Session, key: str, name: str, parent_id: int | None = None) -> RaplaCategory:
    category = create_rapla_category(db, key=key, parent_id=parent_id)

    abbrev = get_language_abbreviation_by_language(db, "en")
    if abbrev is None:
        raise RuntimeError("Missing language abbreviation for 'en'; seeder will not create it")

    language_name = create_language_name(db, cast(int, abbrev.id), name)
    add_language_name_to_category(db, cast(int, category.id), cast(int, language_name.id))

    return category
