from enum import Enum as PyEnum

from sqlalchemy.orm import Session
from app.cruds.crud_title import create_title, get_title_by_name

class TytulEnum(PyEnum):
    MGR = "mgr."
    DR = "dr"
    DR_HAB = "dr hab."
    PROF_DR_HAB = "prof. dr hab."
    MGR_INZ = "mgr. inż."
    DR_INZ = "dr inż."
    DR_HAB_INZ = "dr hab inż."
    PROF_DR_HAB_INZ = "prof. dr hab. inż."


def seed_titles(db: Session) -> None:
    for title in TytulEnum:
        try:
            title_row = get_title_by_name(db, title.value)
            if title_row is None:
                title_row = create_title(db, title.value)
        except ValueError:
            continue

    print("Titles seeded.")