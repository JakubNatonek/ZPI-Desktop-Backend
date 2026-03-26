from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_department_for_category import RaplaDepartmentForCategory


def get_all_department_category_mappings(db: Session) -> List[RaplaDepartmentForCategory]:
    return db.query(RaplaDepartmentForCategory).order_by(RaplaDepartmentForCategory.id.asc()).all()


def get_department_category_mapping_by_id(db: Session, mapping_id: int) -> Optional[RaplaDepartmentForCategory]:
    return db.query(RaplaDepartmentForCategory).filter(RaplaDepartmentForCategory.id == mapping_id).first()


def get_department_category_mappings_by_category(db: Session, category_id: int) -> List[RaplaDepartmentForCategory]:
    return db.query(RaplaDepartmentForCategory).filter(RaplaDepartmentForCategory.id_category == category_id).all()


def get_department_category_mappings_by_department(db: Session, department_id: int) -> List[RaplaDepartmentForCategory]:
    return db.query(RaplaDepartmentForCategory).filter(RaplaDepartmentForCategory.id_department == department_id).all()


def get_department_category_mapping(db: Session, category_id: int, department_id: int) -> Optional[RaplaDepartmentForCategory]:
    return (
        db.query(RaplaDepartmentForCategory)
        .filter(
            RaplaDepartmentForCategory.id_category == category_id,
            RaplaDepartmentForCategory.id_department == department_id,
        )
        .first()
    )


def create_department_category_mapping(db: Session, category_id: int, department_id: int) -> RaplaDepartmentForCategory:
    # prevent duplicate mapping
    existing = get_department_category_mapping(db, category_id, department_id)
    if existing:
        raise ValueError(f"Mapping already exists for category {category_id} and department {department_id}")

    mapping = RaplaDepartmentForCategory(id_category=category_id, id_department=department_id)
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


def delete_department_category_mapping(db: Session, mapping_id: int) -> bool:
    mapping = get_department_category_mapping_by_id(db, mapping_id)
    if mapping is None:
        return False
    db.delete(mapping)
    db.commit()
    return True
