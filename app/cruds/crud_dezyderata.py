from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.model_dezyderata import Dezyderata
from app.models.model_semestr import Semestr
from app.schemas.dezyderata import DezyderataCreate, DezyderataUpdate, SemestrCreate


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


# ----- Dezyderata CRUD -----

def get_dezyderaty(db: Session, user_id: Optional[int] = None, semestr_id: Optional[int] = None) -> List[Dezyderata]:
    query = db.query(Dezyderata)
    if user_id is not None:
        query = query.filter(Dezyderata.user_id == user_id)
    if semestr_id is not None:
        query = query.filter(Dezyderata.semestr_id == semestr_id)
    return query.order_by(Dezyderata.data_od.desc()).all()


def get_dezyderata_by_id(db: Session, dezyderata_id: int) -> Optional[Dezyderata]:
    return db.query(Dezyderata).filter(Dezyderata.id == dezyderata_id).first()


def get_dezyderata_by_user_and_dates(
    db: Session,
    user_id: int,
    data_od: date,
    data_do: date,
    semestr_id: int
) -> Optional[Dezyderata]:
    return db.query(Dezyderata).filter(
        Dezyderata.user_id == user_id,
        Dezyderata.data_od == data_od,
        Dezyderata.data_do == data_do,
        Dezyderata.semestr_id == semestr_id
    ).first()


def create_dezyderata(db: Session, user_id: int, payload: DezyderataCreate) -> Dezyderata:
    dezyderata = Dezyderata(
        user_id=user_id,
        data_od=payload.data_od,
        data_do=payload.data_do,
        godziny=payload.godziny,
        semestr_id=payload.semestr_id
    )
    db.add(dezyderata)
    db.commit()
    db.refresh(dezyderata)
    return dezyderata


def update_dezyderata(db: Session, dezyderata: Dezyderata, payload: DezyderataUpdate) -> Dezyderata:
    dezyderata.data_od = payload.data_od
    dezyderata.data_do = payload.data_do
    dezyderata.godziny = payload.godziny
    dezyderata.semestr_id = payload.semestr_id
    db.commit()
    db.refresh(dezyderata)
    return dezyderata


def upsert_dezyderata(db: Session, user_id: int, payload: DezyderataCreate) -> Dezyderata:
    existing = get_dezyderata_by_user_and_dates(
        db, user_id, payload.data_od, payload.data_do, payload.semestr_id
    )
    if existing:
        existing.godziny = payload.godziny
        db.commit()
        db.refresh(existing)
        return existing
    return create_dezyderata(db, user_id, payload)


def delete_dezyderata(db: Session, dezyderata: Dezyderata) -> None:
    db.delete(dezyderata)
    db.commit()


def map_dezyderata_to_response(dezyderata: Dezyderata) -> dict:
    return {
        "id": dezyderata.id,
        "user_id": dezyderata.user_id,
        "data_od": dezyderata.data_od,
        "data_do": dezyderata.data_do,
        "godziny": dezyderata.godziny,
        "semestr_id": dezyderata.semestr_id,
        "semestr_nazwa": dezyderata.semestr.nazwa if dezyderata.semestr else None
    }


def map_semestr_to_response(semestr: Semestr) -> dict:
    return {
        "id": semestr.id,
        "data_rozpoczecia": semestr.data_rozpoczecia,
        "data_zakonczenia": semestr.data_zakonczenia,
        "nazwa": semestr.nazwa
    }
