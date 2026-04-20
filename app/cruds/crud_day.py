from datetime import  datetime, timedelta
from typing import Set

from sqlalchemy.orm import Session

from app.models.model_day import Day

def get_days(db: Session) -> list[Day]:
    return db.query(Day).order_by(Day.id.asc()).all()

def get_day_by_id(db: Session, day_id: int) -> Day:
    return db.query(Day).filter(Day.id == day_id).first()

# NOTE: This should be in seprate crude file for days
def get_valid_day_ids(db: Session) -> Set[int]:
    return {day.id for day in get_days(db)}

def get_first_day(start: datetime, day_id: int) -> datetime:
    days_ahead = ( (day_id - 1) - start.weekday()) % 7
    return start + timedelta(days = days_ahead)
