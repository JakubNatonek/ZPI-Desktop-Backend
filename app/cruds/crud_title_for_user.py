from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.model_title_for_user import TitleForUser
from app.models.model_title import TitleModel


def get_title_for_user_relation_by_id(db: Session, rel_id: int) -> Optional[TitleForUser]:
    return db.query(TitleForUser).filter(TitleForUser.id == rel_id).first()


def get_all_title_relation_by_user_id(db: Session, user_id: int) -> list[TitleForUser]:
    return db.query(TitleForUser).filter(
        TitleForUser.user_id == user_id,
    ).all()

def list_title_for_user_relations(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[TitleForUser]:
    q = db.query(TitleForUser).order_by(TitleForUser.id.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def list_titles_for_user(db: Session, user_id: int) -> List[TitleModel]:
    return db.query(TitleModel).join(
        TitleForUser,
        TitleModel.id == TitleForUser.title_id,
    ).filter(TitleForUser.user_id == user_id).all()


def get_relation(db: Session, user_id: int, title_id: int) -> Optional[TitleForUser]:
    return db.query(TitleForUser).filter(
        TitleForUser.user_id == user_id,
        TitleForUser.title_id == title_id,
    ).first()


def add_title_to_user(db: Session, user_id: int, title_id: int) -> TitleForUser:
    existing = get_relation(db, user_id, title_id)
    if existing:
        return existing

    rel = TitleForUser(user_id=user_id, title_id=title_id)
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


def remove_title_from_user(db: Session, user_id: int) -> None:
    row = get_title_for_user_relation_by_id(db, user_id)
    if row:
        db.delete(row)
        db.commit()


def remove_relation_by_id(db: Session, rel_id: int) -> None:
    row = get_title_for_user_relation_by_id(db, rel_id)
    if row:
        db.delete(row)
        db.commit()
