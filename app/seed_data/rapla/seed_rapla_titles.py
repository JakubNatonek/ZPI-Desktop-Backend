from sqlalchemy.orm import Session

from typing import cast

from app.models.rapla.model_rapla_category import RaplaCategory
from app.cruds.rapla.crud_rapla_categories import create_rapla_category
from app.cruds.rapla.crud_rapla_language_abbreviations import get_language_abbreviation_by_language
from app.cruds.rapla.crud_rapla_language_name import create_language_name
from app.cruds.rapla.crud_rapla_language_name_for_category import add_language_name_to_category


from enum import Enum as PyEnum

from sqlalchemy.orm import Session
from app.cruds.crud_title import create_title

from app.cruds.rapla.crud_rapla_title_to_category import add_rapla_title_to_category

class TytulEnum(PyEnum):
    MGR = "mgr."
    DR = "dr."
    DR_HAB = "dr. hab."
    PROF_DR_HAB = "prof. dr. hab."
    MGR_INZ = "mgr. inż."
    DR_INZ = "dr. inż."
    DR_HAB_INZ = "dr. hab. inż."
    PROF_DR_HAB_INZ = "prof. dr. hab. inż."

def seed_rapla_titles(db: Session) -> None:
    root = _seed_rapla_titles(db, "Tytuł", "tytul")

    for title in TytulEnum:
        try:
            t = create_title(db, title.value)
            category_title = _seed_rapla_titles(db, key = title.value, name = title.value, parent_id = cast(int, root.id))
            add_rapla_title_to_category(db,  cast(int, category_title.id),  cast(int, t.id))
        except ValueError:
            # role already exists, ignore
            continue

    print("Titles seeded.")


def _seed_rapla_titles(db: Session, key: str, name: str, parent_id: int | None = None) -> RaplaCategory:
    # avoid unique constraint errors by returning existing category if key exists
    category_title = db.query(RaplaCategory).filter(RaplaCategory.key == key).first()
    if category_title is None:
        category_title = create_rapla_category(db, key=key, parent_id=parent_id)

    abbrev = get_language_abbreviation_by_language(db, "en")
    if abbrev is None:
        raise RuntimeError("Missing language abbreviation for 'en'; seeder will not create it")

    language_name = create_language_name(db, cast(int, abbrev.id), name)
    add_language_name_to_category(db, cast(int, category_title.id), cast(int, language_name.id))

    return category_title