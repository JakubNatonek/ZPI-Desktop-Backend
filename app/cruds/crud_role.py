from sqlalchemy.orm import Session

from app.models.model_role import Role


def create_role(db: Session, name: str) -> Role:
    existing = db.query(Role).filter(Role.name == name).first()
    if existing:
        raise ValueError(f"Role already exists: {name}")
    role = Role(name=name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role
