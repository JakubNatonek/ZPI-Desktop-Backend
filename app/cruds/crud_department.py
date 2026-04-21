from typing import Optional, cast
from sqlalchemy.orm import Session

from app.models.model_department import Department
from app.cruds.rapla.crud_rapla_categories import create_rapla_category
from app.cruds.rapla.crud_rapla_department_for_category import create_department_category_mapping


def ensure_department_rapla_category(db: Session, department: Department) -> None:
    root_category = create_rapla_category(
        db,
        key="kod_budynku",
        language_names=[("en", "Kod_budynku")],
    )

    rapla_category = create_rapla_category(
        db,
        key=cast(str, department.abbreviation),
        parent_id=cast(int, root_category.id),
        language_names=[("en", cast(str, department.abbreviation))],
    )

    create_department_category_mapping(
        db,
        cast(int, rapla_category.id),
        cast(int, department.id),
    )


def get_all_departments(db: Session) -> list[Department]:
    return db.query(Department).order_by(Department.id.asc()).all()


def get_department_by_id(db: Session, department_id: int) -> Optional[Department]:
    return db.query(Department).filter(Department.id == department_id).first()


def get_department_by_abbreviation(db: Session, abbreviation: str) -> Optional[Department]:
    return db.query(Department).filter(Department.abbreviation == abbreviation).first()


# NOTE: To delete chek if not used
def get_departments_by_ids(db: Session, department_ids: list[int]) -> list[Department]:
    if not department_ids:
        return []

    return db.query(Department).filter(Department.id.in_(department_ids)).all()


def create_department(db: Session, name: str, abbreviation: str) -> Department:
    # check name uniqueness
    name_exists = db.query(Department).filter(Department.name == name).first()
    if name_exists:
        raise ValueError(f"Department name already exists: {name}")

    # check abbreviation uniqueness
    abbr_exists = db.query(Department).filter(Department.abbreviation == abbreviation).first()
    if abbr_exists:
        raise ValueError(f"Department abbreviation already exists: {abbreviation}")

    department = Department(name=name, abbreviation=abbreviation)
    db.add(department)
    db.commit()
    db.refresh(department)
    ensure_department_rapla_category(db, department)
    return department


def update_department(db: Session, department_id: int, name: Optional[str] = None, abbreviation: Optional[str] = None) -> Optional[Department]:
    department = get_department_by_id(db, department_id)
    if department is None:
        return None

    if name is not None and name != department.name:
        conflict = db.query(Department).filter(Department.name == name, Department.id != department_id).first()
        if conflict:
            raise ValueError(f"Department name already exists: {name}")
        department.name = name # type: ignore

    if abbreviation is not None and abbreviation != department.abbreviation:
        conflict = db.query(Department).filter(Department.abbreviation == abbreviation, Department.id != department_id).first()
        if conflict:
            raise ValueError(f"Department abbreviation already exists: {abbreviation}")
        department.abbreviation = abbreviation # type: ignore

    db.commit()
    db.refresh(department)
    return department


def delete_department(db: Session, department_id: int) -> bool:
    department = get_department_by_id(db, department_id)
    if department is None:
        return False

    db.delete(department)
    db.commit()
    return True
