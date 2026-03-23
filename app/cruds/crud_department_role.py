from sqlalchemy.orm import Session
from app.models.model_user import Department, Role


def create_department(db: Session, name: str) -> Department:
    existing = db.query(Department).filter(Department.name == name).first()
    if existing:
        raise ValueError(f"Department already exists: {name}")
    department = Department(name=name)
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


def create_role(db: Session, name: str) -> Role:
    existing = db.query(Role).filter(Role.name == name).first()
    if existing:
        raise ValueError(f"Role already exists: {name}")
    role = Role(name=name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def get_departments(db: Session) -> list[Department]:
    return db.query(Department).order_by(Department.name.asc()).all()


def get_roles(db: Session) -> list[Role]:
    return db.query(Role).order_by(Role.name.asc()).all()
