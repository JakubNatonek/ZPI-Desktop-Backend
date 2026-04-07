from typing import List

from sqlalchemy.orm import Session

from app.models.model_role_for_user import RolesForUser
from app.models.model_role import Role


def add_role_to_user(db: Session, user_id: int, role_id: int) -> RolesForUser:
    existing = db.query(RolesForUser).filter_by(user_id=user_id, role_id=role_id).first()
    if existing is not None:
        raise ValueError("Role mapping already exists for user")

    mapping = RolesForUser(user_id=user_id, role_id=role_id)
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


def remove_role_from_user(db: Session, user_id: int, role_id: int) -> None:
    mapping = db.query(RolesForUser).filter_by(user_id=user_id, role_id=role_id).first()
    if mapping is None:
        raise ValueError("Role mapping does not exist")
    db.delete(mapping)
    db.commit()


def get_roles_for_user(db: Session, user_id: int) -> List[Role]:
    # Return Role rows for the given user by joining the association table.
    return (
        db.query(Role)
        .join(RolesForUser, RolesForUser.role_id == Role.id)
        .filter(RolesForUser.user_id == user_id)
        .all()
    )
