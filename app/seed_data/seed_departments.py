from enum import Enum as PyEnum

from sqlalchemy.orm import Session

from app.cruds.crud_department import create_department


class DzialEnum(str, PyEnum):
    ADMIN = "Admin"
    NAUK_EKONOMICZNYCH = "Wydział Nauk Ekonomicznych"
    NAUK_HUMANISTYCZNYCH = "Wydział Nauk Humanistycznych"
    NAUK_O_KULTURZE_FIZYCZNEJ_I_BEZPIECZENSTWIE = (
        "Wydział Nauk o Kulturze Fizycznej i Bezpieczeństwie"
    )
    NAUK_SPOLECZNYCH_I_SZTUKI = "Wydział Nauk Społecznych i Sztuki"
    NAUK_INZYNIERYJNYCH = "Wydział Nauk Inżynieryjnych"
    WYDZIAL_LEKARSKI_I_NAUK_O_ZDROWIU = "Wydział Lekarski i Nauk o Zdrowiu"


def seed_departments(db: Session) -> None:
    for dep in DzialEnum:
        try:
            create_department(db, dep.value)
        except ValueError:
            # already exists, ignore
            continue

    print("Departments seeded.")