from datetime import date
from typing import List, Optional, Set

from sqlalchemy.orm import Session

from app.models.model_day import Day
from app.models.model_dezyderata import Dezyderata
from app.models.model_semestr import Semestr
from app.schemas.dezyderata import DezyderataCreate, SemestrCreate


# ----- Semestr CRUD -----

def get_semestry(db: Session) -> List[Semestr]:
    return db.query(Semestr).order_by(Semestr.data_rozpoczecia.desc()).all()


def get_semestr_by_id(db: Session, semestr_id: int) -> Optional[Semestr]:
    return db.query(Semestr).filter(Semestr.id == semestr_id).first()


def get_current_semestr(db: Session, current_date: date = None) -> Optional[Semestr]:
    if current_date is None:
        current_date = date.today()
    return db.query(Semestr).filter(
        Semestr.data_rozpoczecia <= current_date,
        Semestr.data_zakonczenia >= current_date
    ).first()


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


def delete_semestr(db: Session, semestr: Semestr) -> None:
    db.delete(semestr)
    db.commit()


def get_days(db: Session) -> List[Day]:
    return db.query(Day).order_by(Day.id.asc()).all()


def get_valid_day_ids(db: Session) -> Set[int]:
    return {day.id for day in get_days(db)}


# ----- Dezyderata CRUD -----

def get_dezyderaty(db: Session, user_id: Optional[int] = None, semestr_id: Optional[int] = None) -> List[Dezyderata]:
    query = db.query(Dezyderata)
    if user_id is not None:
        query = query.filter(Dezyderata.user_id == user_id)
    if semestr_id is not None:
        query = query.filter(Dezyderata.semestr_id == semestr_id)
    return query.order_by(Dezyderata.data_od.desc(), Dezyderata.day_id.asc(), Dezyderata.from_hour.asc()).all()


def get_dezyderata_by_id(db: Session, dezyderata_id: int) -> Optional[Dezyderata]:
    return db.query(Dezyderata).filter(Dezyderata.id == dezyderata_id).first()


def replace_dezyderata_for_week(db: Session, user_id: int, payload: DezyderataCreate) -> List[Dezyderata]:
    db.query(Dezyderata).filter(
        Dezyderata.user_id == user_id,
        Dezyderata.data_od == payload.data_od,
        Dezyderata.data_do == payload.data_do,
        Dezyderata.semestr_id == payload.semestr_id,
    ).delete(synchronize_session=False)

    created_items: List[Dezyderata] = []
    for entry in payload.entries:
        created = Dezyderata(
            user_id=user_id,
            data_od=payload.data_od,
            data_do=payload.data_do,
            semestr_id=payload.semestr_id,
            day_id=entry.day_id,
            from_hour=entry.from_hour,
            to_hour=entry.to_hour + 1,
            is_available=entry.is_available,
        )
        db.add(created)
        created_items.append(created)

    db.commit()
    for item in created_items:
        db.refresh(item)

    return created_items


def delete_dezyderata(db: Session, dezyderata: Dezyderata) -> None:
    db.delete(dezyderata)
    db.commit()


def map_dezyderata_to_response(dezyderata: Dezyderata) -> dict:
    return {
        "id": dezyderata.id,
        "user_id": dezyderata.user_id,
        "data_od": dezyderata.data_od,
        "data_do": dezyderata.data_do,
        "semestr_id": dezyderata.semestr_id,
        "day_id": dezyderata.day_id,
        "from_hour": dezyderata.from_hour,
        "to_hour": dezyderata.to_hour,
        "is_available": dezyderata.is_available,
        "day_name": dezyderata.day.name if dezyderata.day else None,
        "semestr_nazwa": dezyderata.semestr.nazwa if dezyderata.semestr else None
    }


def map_semestr_to_response(semestr: Semestr) -> dict:
    return {
        "id": semestr.id,
        "data_rozpoczecia": semestr.data_rozpoczecia,
        "data_zakonczenia": semestr.data_zakonczenia,
        "nazwa": semestr.nazwa
    }
