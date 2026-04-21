from typing import List, Optional, cast

from sqlalchemy.orm import Session

from app.models.model_title import TitleModel
from app.cruds.rapla.crud_rapla_categories import create_rapla_category
from app.cruds.rapla.crud_rapla_title_to_category import add_rapla_title_to_category


def ensure_title_rapla_category(db: Session, title: TitleModel) -> None:
    root_category = create_rapla_category(
        db,
        key="tytul",
        language_names=[("en", "Tytuł")],
    )

    title_category = create_rapla_category(
        db,
        key=cast(str, title.name),
        parent_id=cast(int, root_category.id),
        language_names=[("en", cast(str,title.name))],
    )

    add_rapla_title_to_category(db, cast(int,title_category.id), cast(int,title.id))


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
    ensure_title_rapla_category(db, t)
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