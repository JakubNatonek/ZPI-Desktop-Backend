from typing import Optional

from sqlalchemy.orm import Session

from app.models.model_activity import Activity
from app.models.rapla.model_rapla_activity_to_category import RaplaActivityToCategory
from app.models.rapla.model_rapla_category import RaplaCategory


def get_activity_category_mapping_by_id(db: Session, mapping_id: int) -> Optional[RaplaActivityToCategory]:
    return (
        db.query(RaplaActivityToCategory)
        .filter(RaplaActivityToCategory.id == mapping_id)
        .first()
    )


def get_activity_category_mapping(
    db: Session,
    activity_id: int,
    category_id: int,
) -> Optional[RaplaActivityToCategory]:
    return (
        db.query(RaplaActivityToCategory)
        .filter(
            RaplaActivityToCategory.activity_id == activity_id,
            RaplaActivityToCategory.category_id == category_id,
        )
        .first()
    )


def get_categories_for_activity_id(
    db: Session,
    activity_id: int,
) -> list[RaplaCategory]:
    return (
        db.query(RaplaCategory)
        .join(RaplaActivityToCategory, RaplaCategory.id == RaplaActivityToCategory.category_id)
        .filter(RaplaActivityToCategory.activity_id == activity_id)
        .order_by(RaplaActivityToCategory.id.asc())
        .all()
    )


def get_activities_for_category_id(
    db: Session,
    category_id: int,
) -> list[Activity]:
    return (
        db.query(Activity)
        .join(RaplaActivityToCategory, Activity.id == RaplaActivityToCategory.activity_id)
        .filter(RaplaActivityToCategory.category_id == category_id)
        .order_by(RaplaActivityToCategory.id.asc())
        .all()
    )


def create_activity_category_mapping(
    db: Session,
    activity_id: int,
    category_id: int,
) -> RaplaActivityToCategory:
    existing = get_activity_category_mapping(db, activity_id, category_id)
    if existing is not None:
        return existing

    mapping = RaplaActivityToCategory(
        activity_id=activity_id,
        category_id=category_id,
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


def delete_activity_category_mapping(db: Session, mapping_id: int) -> bool:
    mapping = get_activity_category_mapping_by_id(db, mapping_id)
    if mapping is None:
        return False

    db.delete(mapping)
    db.commit()
    return True
