from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.model_title import TitleModel


def get_title_by_id(db: Session, title_id: int) -> Optional[TitleModel]:
    return db.query(TitleModel).filter(TitleModel.id == title_id).first()


def get_title_by_name(db: Session, name: str) -> Optional[TitleModel]:
    return db.query(TitleModel).filter(TitleModel.name == name).first()


def list_titles(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[TitleModel]:
    q = db.query(TitleModel).order_by(TitleModel.name.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def create_title(db: Session, name: str) -> TitleModel:
    """Create a title. Raises ValueError if a title with same name already exists."""
    existing = get_title_by_name(db, name)
    if existing is not None:
        raise ValueError(f"Title already exists: {name}")

    t = TitleModel(name=name)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def delete_title(db: Session, title: TitleModel) -> None:
    db.delete(title)
    db.commit()


def delete_title_by_id(db: Session, title_id: int) -> bool:
    t = get_title_by_id(db, title_id)
    if t is None:
        return False
    db.delete(t)
    db.commit()
    return True
