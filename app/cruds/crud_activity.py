from typing import Optional

from sqlalchemy.orm import Session

from app.models.model_activity import Activity
from app.schemas.rapla.schema_rapla_categories import RaplaCategory
from app.cruds.rapla.crud_rapla_categories import get_rapla_category_by_key

def get_all_activities(db: Session) -> list[Activity]:
    return db.query(Activity).order_by(Activity.name.asc()).all()


def get_activity_by_id(db: Session, activity_id: int) -> Optional[Activity]:
    return db.query(Activity).filter(Activity.id == activity_id).first()


def get_activities_by_ids(db: Session, activity_ids: list[int]) -> list[Activity]:
    if not activity_ids:
        return []

    return db.query(Activity).filter(Activity.id.in_(activity_ids)).all()


def get_activity_by_name(db: Session, name: str) -> Optional[Activity]:
    cleaned_name = name.strip()
    if not cleaned_name:
        return None

    return db.query(Activity).filter(Activity.name == cleaned_name).first()


def create_activity(db: Session, name: str) -> Activity:
    activity = Activity(name=name.strip())
    db.add(activity)
    db.flush()
    return activity


def get_or_create_activity(db: Session, name: str) -> Activity:
    activity = get_activity_by_name(db, name)
    if activity is not None:
        return activity

    return create_activity(db, name)


def update_activity(db: Session, activity_id: int, name: str) -> Optional[Activity]:
    activity = get_activity_by_id(db, activity_id)
    if activity is None:
        return None

    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Activity name cannot be empty")

    existing = get_activity_by_name(db, cleaned_name)
    if existing is not None and existing.id != activity_id:
        raise ValueError(f"Activity name already exists: {cleaned_name}")

    activity.name = cleaned_name
    db.commit()
    db.refresh(activity)
    return activity


def delete_activity(db: Session, activity_id: int) -> bool:
    activity = get_activity_by_id(db, activity_id)
    if activity is None:
        return False

    db.delete(activity)
    db.commit()
    return True