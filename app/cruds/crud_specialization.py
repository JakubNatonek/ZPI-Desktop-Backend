from sqlalchemy.orm import Session, joinedload

from app.models.model_group import Group


def get_all_specializations(db: Session) -> list[Group]:
    return (
        db.query(Group)
        .options(joinedload(Group.department))
        .order_by(Group.specialization.asc())
        .all()
    )


def create_specialization(db: Session, code: str, name: str, department_id: int) -> Group:
    existing = (
        db.query(Group)
        .filter((Group.code == code) | (Group.specialization == name))
        .first()
    )
    if existing:
        raise ValueError("Specjalność o podanym identyfikatorze lub nazwie już istnieje.")

    group = Group(
        specialization=name,
        code=code,
        department_id=department_id,
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def delete_specialization(db: Session, spec_id: int) -> bool:
    group = db.query(Group).filter(Group.id == spec_id).first()
    if group is None:
        return False
    db.delete(group)
    db.commit()
    return True
