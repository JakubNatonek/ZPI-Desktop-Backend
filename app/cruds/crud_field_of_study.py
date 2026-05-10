from typing import Optional

from sqlalchemy.orm import Session

from app.models.model_field_of_study import FieldOfStudy


def get_field_of_study_by_id(db: Session, field_of_study_id: int) -> Optional[FieldOfStudy]:
    return db.query(FieldOfStudy).filter(FieldOfStudy.id == field_of_study_id).first()


def get_field_of_study_by_abbrevation(db: Session, abbrevation: str) -> Optional[FieldOfStudy]:
    return db.query(FieldOfStudy).filter(FieldOfStudy.abbrevation == abbrevation).first()


def create_field_of_study(db: Session, name: str, abbrevation: str, year: int) -> FieldOfStudy:
    field_of_study = FieldOfStudy(
        name=name,
        abbrevation=abbrevation,
        year=year,
    )
    db.add(field_of_study)
    db.flush()
    return field_of_study


def get_field_of_study_by_abbrevation_and_year(db: Session, abbrevation: str, year: int) -> Optional[FieldOfStudy]:
    try:
        return (
            db.query(FieldOfStudy)
            .filter(FieldOfStudy.abbrevation == abbrevation)
            .filter(FieldOfStudy.year == int(year))
            .first()
        )
    except Exception:
        return None
