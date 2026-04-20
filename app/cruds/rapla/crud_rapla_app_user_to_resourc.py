from sqlalchemy.orm import Session

from typing import cast

from app.models.rapla.model_rapla_app_user_to_resourc import RaplaAppUserToResourc
from app.models.rapla.model_rapla_resourc import ModelRaplaResourc
from app.models.model_user import User as AppUser

from app.schemas.rapla.resorces.schema_rapla_resourc_nauczyciel import (
    SchemaRaplaResourcNauczyciel,
)
from app.schemas.rapla.schema_interface_rapla_resorc import SchemaInterfaceRaplaResourc
from app.cruds.rapla.rapla_format_datetime import format_rapla_datetime
from app.cruds.crud_title_for_user import get_title_for_user

from app.cruds.rapla.crud_rapla_title_to_category import get_rapla_categories_for_title
from app.cruds.crud_departments_for_user import get_departments_for_user
from app.cruds.rapla.crud_rapla_department_for_category import  get_department_category_by_department_id
from app.cruds.rapla.crud_rapla_permission_for_resourc import get_permission_by_resourc_id
from app.cruds.rapla.crud_rapla_permission import get_permission_schema_by_model

from app.schemas.rapla.schema_rapla_permision import RaplaPermission as RaplaPermissionSchema

from datetime import datetime



def list_app_user_to_resourc_mappings(db: Session) -> list[RaplaAppUserToResourc]:
    return db.query(RaplaAppUserToResourc).order_by(RaplaAppUserToResourc.id.asc()).all()

def get_resorsc_by_user_id(db: Session, app_user_id: int) -> ModelRaplaResourc | None:
    mapping = (
        db.query(RaplaAppUserToResourc)
        .filter(RaplaAppUserToResourc.app_user_id == app_user_id)
        .first()
    )
    if mapping is None or mapping.rapla_resourc_id is None:
        return None

    return db.query(ModelRaplaResourc).filter(ModelRaplaResourc.id == mapping.rapla_resourc_id).first()


def get_mapping_by_app_user_and_resourc(db: Session, app_user_id: int, rapla_resourc_id: int) -> RaplaAppUserToResourc | None:
    return (
        db.query(RaplaAppUserToResourc)
        .filter(RaplaAppUserToResourc.app_user_id == app_user_id)
        .filter(RaplaAppUserToResourc.rapla_resourc_id == rapla_resourc_id)
        .first()
    )


def create_app_user_to_resourc_mapping(db: Session, app_user_id: int, rapla_resourc_id: int) -> RaplaAppUserToResourc:
    existing = get_mapping_by_app_user_and_resourc(db, app_user_id, rapla_resourc_id)
    if existing is not None:
        return existing

    m = RaplaAppUserToResourc(app_user_id=app_user_id, rapla_resourc_id=rapla_resourc_id)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def delete_app_user_to_resourc_mapping(db: Session, app_user_id: int, rapla_resourc_id: int) -> bool:
    mapping = get_mapping_by_app_user_and_resourc(db, app_user_id, rapla_resourc_id)
    if mapping is None:
        return False
    db.delete(mapping)
    db.commit()
    return True


def all_app_user_to_resourc_schema(db: Session) -> list[SchemaRaplaResourcNauczyciel]:
    mappings = list_app_user_to_resourc_mappings(db)
    schemas: list[SchemaRaplaResourcNauczyciel] = []
    for m in mappings:
        try:
            schemas.append(app_user_to_resourc_schema(db, cast(int, m.app_user_id)))
        except Exception:
            # skip entries that cannot be converted
            continue
    return schemas

def app_user_to_resourc_schema(db: Session, app_user_id: int) -> SchemaRaplaResourcNauczyciel:
    from app.cruds.crud_user import get_user_by_id
    resource = get_resorsc_by_user_id(db, app_user_id)
    app_user = get_user_by_id(db, app_user_id)
    title = get_title_for_user(db, app_user_id)
    title_category = get_rapla_categories_for_title(db, cast(int, title.id) )
    
    permisions_model = get_permission_by_resourc_id(db, cast(int, resource.id ))

    permisions_schema: list[RaplaPermissionSchema] = []
    for permision_model in permisions_model:
        permision_schema = get_permission_schema_by_model(db, permision_model)
        if permision_schema is not None:
            permisions_schema.append(permision_schema)

    departments = get_departments_for_user(db, app_user_id)

    departments_names: list[str] = []
    for department in departments:
        department_category= get_department_category_by_department_id(db, cast(int, department.id ))
        departments_names.append( cast(str, department_category.key) )

    #print(cast(str, resource.uuid))
    # build schema
    schema = SchemaRaplaResourcNauczyciel(
        uuid = cast(str, resource.uuid),
        owner = cast(str, resource.owner),
        created_at = format_rapla_datetime(cast(datetime, resource.created_at) ),
        last_changed = format_rapla_datetime(cast(datetime, resource.last_changed) ),
        last_changed_by = cast(str, resource.last_changed_by),
        first_name = cast(str, app_user.first_name),
        last_name = cast(str, app_user.last_name),
        title = cast(str, title_category.key ) or None,
        departments = departments_names,
        permissions = permisions_schema
    )

    return schema