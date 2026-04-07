from typing import List

from sqlalchemy.orm import Session

from app.models.model_department_for_user import DepartmentsForUser
from app.models.model_department import Department


def add_department_to_user(db: Session, user_id: int, department_id: int) -> DepartmentsForUser:
    existing = db.query(DepartmentsForUser).filter_by(user_id=user_id, department_id=department_id).first()
    if existing is not None:
        raise ValueError("Department mapping already exists for user")

    mapping = DepartmentsForUser(user_id=user_id, department_id=department_id)
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


def remove_department_from_user(db: Session, user_id: int, department_id: int) -> None:
    mapping = db.query(DepartmentsForUser).filter_by(user_id=user_id, department_id=department_id).first()
    if mapping is None:
        raise ValueError("Department mapping does not exist")
    db.delete(mapping)
    db.commit()


def get_departments_for_user(db: Session, user_id: int) -> List[Department]:
    # Query departments via the association table instead of relying on
    # a relationship attribute on User (which may not be defined).
    return (
        db.query(Department)
        .join(DepartmentsForUser, DepartmentsForUser.department_id == Department.id)
        .filter(DepartmentsForUser.user_id == user_id)
        .all()
    )
