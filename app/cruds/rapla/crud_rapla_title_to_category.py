from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_title_to_category import RaplaTitleToCategory
from app.models.model_title import TitleModel
from app.models.rapla.model_rapla_category import RaplaCategory


def get_rapla_title_to_category_by_id(db: Session, rel_id: int) -> Optional[RaplaTitleToCategory]:
    return db.query(RaplaTitleToCategory).filter(RaplaTitleToCategory.id == rel_id).first()


def get_rapla_title_to_category_relation(db: Session, category_id: int, title_id: int) -> Optional[RaplaTitleToCategory]:
    return db.query(RaplaTitleToCategory).filter(
        RaplaTitleToCategory.id_category == category_id,
        RaplaTitleToCategory.id_title == title_id,
    ).first()

def get_rapla_title_to_category_relation_by_category_id(db: Session, category_id: int) -> Optional[RaplaTitleToCategory]:
    return db.query(RaplaTitleToCategory).filter(
        RaplaTitleToCategory.id_category == category_id,
    ).first()



def list_rapla_title_to_category_relations(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[RaplaTitleToCategory]:
    q = db.query(RaplaTitleToCategory).order_by(RaplaTitleToCategory.id.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def list_titles_for_rapla_category(db: Session, category_id: int) -> List[TitleModel]:
    return db.query(TitleModel).join(
        RaplaTitleToCategory,
        TitleModel.id == RaplaTitleToCategory.id_title,
    ).filter(RaplaTitleToCategory.id_category == category_id).all()


def list_rapla_categories_for_title(db: Session, title_id: int) -> List[RaplaCategory]:
    return db.query(RaplaCategory).join(
        RaplaTitleToCategory,
        RaplaCategory.id == RaplaTitleToCategory.id_category,
    ).filter(RaplaTitleToCategory.id_title == title_id).all()


def add_rapla_title_to_category(db: Session, category_id: int, title_id: int) -> RaplaTitleToCategory:
    existing = get_rapla_title_to_category_relation(db, category_id, title_id)
    if existing:
        return existing

    rel = RaplaTitleToCategory(id_category=category_id, id_title=title_id)
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


def remove_rapla_title_from_category(db: Session, category_id: int) -> None:
    row = get_rapla_title_to_category_relation_by_category_id(db, category_id)
    if row:
        db.delete(row)
        db.commit()


def remove_rapla_title_to_category_by_id(db: Session, rel_id: int) -> None:
    row = get_rapla_title_to_category_by_id(db, rel_id)
    if row:
        db.delete(row)
        db.commit()
