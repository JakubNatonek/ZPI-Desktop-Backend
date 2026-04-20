from sqlalchemy.orm import Session

from typing import cast

from app.models.rapla.model_rapla_category import RaplaCategory
from app.cruds.rapla.crud_rapla_categories import create_rapla_category
from app.cruds.rapla.crud_rapla_language_abbreviations import get_language_abbreviation_by_language
from app.cruds.rapla.crud_rapla_language_name import create_language_name
from app.cruds.rapla.crud_rapla_language_name_for_category import add_language_name_to_category


def seed_rapla_category_parent(db: Session) -> None:
    _seed_rapla_category_parent(db, "typy_przedmiotow", "typy_przedmiotow")
    


def _seed_rapla_category_parent(db: Session, key: str, name: str, parent_id: int | None = None) -> RaplaCategory:
    # avoid unique constraint errors by returning existing category if key exists
    category = db.query(RaplaCategory).filter(RaplaCategory.key == key).first()
    if category is None:
        category = create_rapla_category(db, key=key, parent_id=parent_id)

    abbrev = get_language_abbreviation_by_language(db, "en")
    if abbrev is None:
        raise RuntimeError("Missing language abbreviation for 'en'; seeder will not create it")

    language_name = create_language_name(db, cast(int, abbrev.id), name)
    add_language_name_to_category(db, cast(int, category.id), cast(int, language_name.id))

    return category
