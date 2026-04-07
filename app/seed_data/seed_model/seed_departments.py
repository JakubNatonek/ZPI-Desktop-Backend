from enum import Enum as PyEnum

from sqlalchemy.orm import Session

from app.models.model_department import Department


class DzialEnum(PyEnum):
    ADMIN = ("Admin", "ADM")
    NAUK_EKONOMICZNYCH = ("Wydzial Nauk Ekonomicznych", "WE")
    NAUK_HUMANISTYCZNYCH = ("Wydzial Nauk Humanistycznych", "WH")
    NAUK_O_KULTURZE_FIZYCZNEJ_I_BEZPIECZENSTWIE = (
        "Wydzial Nauk o Kulturze Fizycznej i Bezpieczenstwie",
        "WKFiB",
    )
    NAUK_SPOLECZNYCH_I_SZTUKI = ("Wydzial Nauk Spolecznych i Sztuki", "WSiS")
    NAUK_INZYNIERYJNYCH = ("Wydzial Nauk Inzynieryjnych", "WI")
    WYDZIAL_LEKARSKI_I_NAUK_O_ZDROWIU = ("Wydzial Lekarski i Nauk o Zdrowiu", "WLiZ")
    INFORMATYKA = ("Informatyka", "INF")
    FIZYKA = ("Fizyka", "FIZ")
    MATEMATYKA = ("Matematyka", "MAT")
    ELEKTRONIKA = ("Elektronika", "ELE")


def seed_departments(db: Session) -> None:
    for dep in DzialEnum:
        name, abbr = dep.value
        existing = db.query(Department).filter(Department.name == name).first()
        if existing is not None:
            continue

        db.add(Department(name=name, abbreviation=abbr))

    db.commit()
    print("Departments seeded.")