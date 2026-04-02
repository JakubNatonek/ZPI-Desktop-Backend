from enum import Enum as PyEnum

from sqlalchemy.orm import Session
from app.cruds.crud_title import create_title

class TytulEnum(PyEnum):
    MGR = "mgr."
    DR = "dr."
    DR_HAB = "dr. hab."
    PROF_DR_HAB = "prof. dr. hab."
    MGR_INZ = "mgr. inż."
    DR_INZ = "dr. inż."
    DR_HAB_INZ = "dr. hab. inż."
    PROF_DR_HAB_INZ = "prof. dr. hab. inż."


def seed_Tytles(db: Session) -> None:
    for title in TytulEnum:
        try:
            create_title(db, title.value)
        except ValueError:
            # role already exists, ignore
            continue

    print("Titles seeded.")