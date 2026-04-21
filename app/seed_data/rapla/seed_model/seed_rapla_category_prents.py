from sqlalchemy.orm import Session

from app.cruds.rapla.crud_rapla_categories import create_rapla_category


def seed_rapla_category_parent(db: Session) -> None:
    create_rapla_category(
        db,
        key="typy_przedmiotow",
        language_names=[("en", "typy_przedmiotow")],
    )
    create_rapla_category(
        db,
        key="kod_budynku",
        language_names=[("en", "Kod_budynku")],
    )
    create_rapla_category(
        db,
        key="tytul",
        language_names=[("en", "Tytuł")],
    )
