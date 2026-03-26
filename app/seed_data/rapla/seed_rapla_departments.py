from sqlalchemy.orm import Session

from typing import cast

from app.models.rapla.model_rapla_category import RaplaCategory
from app.cruds.rapla.crud_rapla_categories import create_rapla_category
from app.cruds.rapla.crud_rapla_language_abbreviations import get_language_abbreviation_by_language
from app.cruds.rapla.crud_rapla_language_name import create_language_name
from app.cruds.rapla.crud_rapla_language_name_for_category import add_language_name_to_category

from app.seed_data.seed_departments import DzialEnum
from app.cruds.crud_department import get_department_by_abbreviation
from app.cruds.rapla.crud_rapla_department_for_category import create_department_category_mapping


def seed_rapla_departments(db: Session) -> None:
    root = _seed_rapla_departments(db, "Kod_budynku", "kod_budynku")

    for dep in DzialEnum:
        _, abbr = dep.value
        key = abbr
        try:
            category = _seed_rapla_departments(db, key=key, name=key, parent_id=cast(int, root.id))
        except Exception:
            # category exists or other error, try to continue
            # attempt to fetch existing category by key would be better, but keep simple
            continue

        dept = get_department_by_abbreviation(db, abbr)
        if dept is None:
            # department not found; skip mapping
            continue
        try:
            create_department_category_mapping(db, cast(int, category.id), cast(int, dept.id))
        except ValueError:
            # mapping already exists, ignore
            continue

def _seed_rapla_departments(db: Session, key: str, name: str, parent_id: int | None = None) -> RaplaCategory:
    # avoid unique constraint errors by returning existing category if key exists
    category_department = db.query(RaplaCategory).filter(RaplaCategory.key == key).first()
    if category_department is None:
        category_department = create_rapla_category(db, key=key, parent_id=parent_id)

    abbrev = get_language_abbreviation_by_language(db, "en")
    if abbrev is None:
        raise RuntimeError("Missing language abbreviation for 'en'; seeder will not create it")

    language_name = create_language_name(db, cast(int, abbrev.id), name)
    add_language_name_to_category(db, cast(int, category_department.id), cast(int, language_name.id))

    return category_department


