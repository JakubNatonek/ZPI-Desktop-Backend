from enum import Enum as PyEnum

from sqlalchemy.orm import Session

from app.cruds.crud_department import create_department


class DzialEnum(PyEnum):
    ADMIN = ("Admin", "ADM")
    NAUK_EKONOMICZNYCH = ("Wydział Nauk Ekonomicznych", "WE")
    NAUK_HUMANISTYCZNYCH = ("Wydział Nauk Humanistycznych", "WH")
    NAUK_O_KULTURZE_FIZYCZNEJ_I_BEZPIECZENSTWIE = (
        "Wydział Nauk o Kulturze Fizycznej i Bezpieczeństwie", 
        "WKFiB"
    )
    NAUK_SPOLECZNYCH_I_SZTUKI = ("Wydział Nauk Społecznych i Sztuki", "WSiS")
    NAUK_INZYNIERYJNYCH = ("Wydział Nauk Inżynieryjnych", "WI")
    WYDZIAL_LEKARSKI_I_NAUK_O_ZDROWIU = ("Wydział Lekarski i Nauk o Zdrowiu", "WLiZ")


def seed_departments(db: Session) -> None:
    for dep in DzialEnum:
        name, abbr = dep.value
        try:
            create_department(db, name, abbr)
        except ValueError:
            # already exists, ignore
            continue

    print("Departments seeded.")