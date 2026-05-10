from sqlalchemy.orm import Session
from typing import cast

from app.models.model_group import Group
from app.cruds.rapla.crud_rapla_resourc import create_resourc
from app.cruds.rapla.crud_rapla_group_to_resourc import create_group_to_resourc_mapping
from app.cruds.crud_field_of_study_for_group import get_field_of_study_from_maping_by_group_id
from app.cruds.crud_department_for_field_of_study import get_departments_for_field_of_study
from app.models.rapla.model_rapla_resourc import ModelRaplaResourc
from app.cruds.rapla.crud_rapla_permission import (
    get_permission_by_access,
    get_permission_by_access_and_group,
    create_permission,
)
from app.cruds.rapla.crud_rapla_permission_for_resourc import create_permission_for_resourc
from app.models.model_department import Department

def _ensure_department_permissions_for_resource(
    db: Session,
    res: ModelRaplaResourc | None,
    departments: list[Department],
) -> None:
    if res is None or res.id is None:
        return

    for department in departments:
        abbreviation = cast(str | None, getattr(department, "abbreviation", None))
        if not abbreviation:
            continue

        group = f"category[key='{abbreviation}_Editor']"
        perm = get_permission_by_access_and_group(db, "allocate_conflicts", group)
        if perm is None:
            perm = create_permission(db, access="allocate_conflicts", group=group)

        try:
            create_permission_for_resourc(db, cast(int, res.id), cast(int, perm.id))
        except Exception:
            continue
        
    perm = get_permission_by_access(db, access="read_no_allocation")
    if perm is None:
        perm = create_permission(db, access="read_no_allocation")
    try:
        create_permission_for_resourc(db, cast(int, res.id), cast(int, perm.id))
    except Exception as e:
        print(f"Failed to assign permission to rapla_resourc id={res.id}: {e}")


def create_group(db: Session, code: str) -> Group:
    group = Group(code=code)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def ensure_resourc(db: Session, group: Group) -> None:
    res = create_resourc(db)
    create_group_to_resourc_mapping(db, group_id=group.id, rapla_resourc_id=res.id)
    department = get_departments_for_field_of_study(db, get_field_of_study_from_maping_by_group_id(db, group.id).id)
    _ensure_department_permissions_for_resource(db, res, department)




def get_group(db: Session) -> list[Group]:
    return db.query(Group).all()

def get_group_by_id(db: Session, id:int) -> Group | None:
    return db.query(Group).filter(Group.id == id).first()
