from datetime import datetime
from typing import cast

from sqlalchemy.orm import Session

from app.models.model_group import Group
from app.models.rapla.model_rapla_resourc import ModelRaplaResourc
from app.models.rapla.model_rapla_group_to_resourc import RaplaGroupToResourc
from app.schemas.rapla.resorces.schema_rapla_resourc_grupa import SchemaRaplaResourcGrupa
from app.schemas.rapla.schema_rapla_permision import RaplaPermission as RaplaPermissionSchema
from app.cruds.rapla.crud_rapla_permission_for_resourc import get_permission_by_resourc_id
from app.cruds.rapla.crud_rapla_permission import get_permission_schema_by_model
from app.cruds.rapla.rapla_format_datetime import format_rapla_datetime
from app.cruds.crud_field_of_study_for_group import get_field_of_study_from_maping_by_group_id
from app.cruds.crud_department_for_field_of_study import get_departments_for_field_of_study

def list_group_to_resourc_mappings(db: Session) -> list[RaplaGroupToResourc]:
    return db.query(RaplaGroupToResourc).order_by(RaplaGroupToResourc.id.asc()).all()


def get_resourc_by_group_id(db: Session, group_id: int) -> ModelRaplaResourc | None:
    mapping = (
        db.query(RaplaGroupToResourc)
        .filter(RaplaGroupToResourc.group_id == group_id)
        .first()
    )
    if mapping is None:
        return None

    return db.query(ModelRaplaResourc).filter(ModelRaplaResourc.id == mapping.rapla_resourc_id).first()


def get_group_by_resourc_id(db: Session, rapla_resourc_id: int) -> Group | None:
    mapping = (
        db.query(RaplaGroupToResourc)
        .filter(RaplaGroupToResourc.rapla_resourc_id == rapla_resourc_id)
        .first()
    )
    if mapping is None:
        return None

    return db.query(Group).filter(Group.id == mapping.group_id).first()


def get_mapping_by_group_and_resourc(db: Session, group_id: int, rapla_resourc_id: int) -> RaplaGroupToResourc | None:
    return (
        db.query(RaplaGroupToResourc)
        .filter(RaplaGroupToResourc.group_id == group_id)
        .filter(RaplaGroupToResourc.rapla_resourc_id == rapla_resourc_id)
        .first()
    )


def create_group_to_resourc_mapping(db: Session, group_id: int, rapla_resourc_id: int) -> RaplaGroupToResourc:
    existing = get_mapping_by_group_and_resourc(db, group_id, rapla_resourc_id)
    if existing is not None:
        return existing

    mapping = RaplaGroupToResourc(group_id=group_id, rapla_resourc_id=rapla_resourc_id)
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


def delete_group_to_resourc_mapping(db: Session, group_id: int, rapla_resourc_id: int) -> bool:
    mapping = get_mapping_by_group_and_resourc(db, group_id, rapla_resourc_id)
    if mapping is None:
        return False

    db.delete(mapping)
    db.commit()
    return True


def group_to_resourc_schema(db: Session, group: Group) -> SchemaRaplaResourcGrupa | None:
    group_id = cast(int | None, group.id)
    if group_id is None:
        return None

    resource = get_resourc_by_group_id(db, group_id)
    if resource is None:
        return None

    permission_models = get_permission_by_resourc_id(db, cast(int, resource.id)) or []
    permission_schemas: list[RaplaPermissionSchema] = []
    for permission_model in permission_models:
        permission_schema = get_permission_schema_by_model(db, permission_model)
        if permission_schema is not None:
            permission_schemas.append(permission_schema)

    # Prefer explicit fields when available; fallback to code for name
    name = cast(str | None, getattr(group, "name", None)) or cast(str | None, getattr(group, "code", None))

    field_of_study = get_field_of_study_from_maping_by_group_id(db, group_id)


    kierunek = cast(str | None, getattr(field_of_study, "abbrevation", None))
    rok_val = getattr(field_of_study, "year", None)

    return SchemaRaplaResourcGrupa(
        uuid=cast(str, resource.uuid),
        owner=cast(str, resource.owner),
        created_at=format_rapla_datetime(cast(datetime, resource.created_at)),
        last_changed=format_rapla_datetime(cast(datetime, resource.last_changed)),
        last_changed_by=cast(str, resource.last_changed_by),
        name=name,
        kierunek=kierunek,
        rok=str(rok_val) if rok_val is not None else None,
        permissions=permission_schemas,
    )


def all_group_to_resourc_schema(db: Session) -> list[SchemaRaplaResourcGrupa]:
    groups = db.query(Group).order_by(Group.code.asc()).all()
    schemas: list[SchemaRaplaResourcGrupa] = []
    for group in groups:
        try:
            group_schema = group_to_resourc_schema(db, group)
            if group_schema is not None:
                schemas.append(group_schema)
        except Exception:
            continue

    return schemas
