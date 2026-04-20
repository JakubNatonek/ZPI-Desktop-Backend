from sqlalchemy.orm import Session
from typing import  Optional
from datetime import date

from app.models.model_semestr import Semestr
from app.schemas.dezyderata import SemestrCreate


def get_semestry(db: Session) -> list[Semestr]:
    return db.query(Semestr).order_by(Semestr.data_rozpoczecia.desc()).all()


def get_semestr_by_id(db: Session, semestr_id: int) -> Optional[Semestr]:
    return db.query(Semestr).filter(Semestr.id == semestr_id).first()


def get_current_semestr(db: Session, current_date: date | None= None) -> Optional[Semestr]:
    if current_date is None:
        current_date = date.today()
    return db.query(Semestr).filter(
        Semestr.data_rozpoczecia <= current_date,
        Semestr.data_zakonczenia >= current_date
    ).first()

# NOTE: Chenge this to field to field insted of payload
def create_semestr(db: Session, payload: SemestrCreate) -> Semestr:
    semestr = Semestr(
        data_rozpoczecia=payload.data_rozpoczecia,
        data_zakonczenia=payload.data_zakonczenia,
        nazwa=payload.nazwa
    )
    db.add(semestr)
    db.commit()
    db.refresh(semestr)
    return semestr

# NOTE: Need this by id
def delete_semestr(db: Session, semestr: Semestr) -> None:
    db.delete(semestr)
    db.commit()

