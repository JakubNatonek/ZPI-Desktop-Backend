from sqlalchemy.orm import Session

from app.models.model_department import Department


def create_department(db: Session, name: str) -> Department:
    existing = db.query(Department).filter(Department.name == name).first()
    if existing:
        raise ValueError(f"Department already exists: {name}")
    department = Department(name=name)
    db.add(department)
    db.commit()
    db.refresh(department)
    return department
