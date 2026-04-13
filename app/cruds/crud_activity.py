from typing import Optional

from sqlalchemy.orm import Session

from app.models.model_activity import Activity


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