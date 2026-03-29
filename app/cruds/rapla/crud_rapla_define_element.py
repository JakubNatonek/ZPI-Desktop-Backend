from typing import List, Optional
from datetime import datetime, timezone
from uuid import uuid4
from typing import cast

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_define_element import RaplaDefineElement
from app.schemas.rapla.schema_rapla_define_element import DefineElement as DefineElementSchema
from app.schemas.rapla.schema_rapla_annotations import RaplaAnnotations as RaplaAnnotationsSchema
from app.schemas.rapla.schema_rapla_language_name import RaplaLanguageName as RaplaLanguageNameSchema
from app.schemas.rapla.schema_rapla_annotation import RaplaAnnotation as RaplaAnnotationSchema
from app.schemas.rapla.schema_rapla_annotations import RaplaAnnotations as RaplaAnnotationsSchema
from app.schemas.rapla.schema_rapla_optional import RaplaOptional as RaplaOptionalSchema
from app.schemas.rapla.schema_rapla_define import Define as DefineSchema

# helpers
from app.cruds.rapla.crud_rapla_language_name_for_define_element import list_language_names_for_define_element
from app.cruds.rapla.crud_rapla_language_name import get_language_name_schema_by_id
from app.cruds.rapla.crud_rapla_annotation_for_define_element import list_relations_for_define_element as list_annotation_relations
from app.cruds.rapla.crud_rapla_annotation import get_annotation_schema_by_id
from app.cruds.rapla.crud_rapla_optional_element_for_define_element import list_relations_for_define_element as list_optional_relations_for_define_element
from app.cruds.rapla.crud_rapla_optional_element import get_optional_element_full_schema_by_id
from app.cruds.rapla.rapla_format_datetime import format_rapla_datetime
from app.schemas.rapla.schema_rapla_permision import RaplaPermission as RaplaPermissionSchema
from app.cruds.rapla.crud_rapla_permission_for_define_element import list_permissions_for_define_element
from app.cruds.rapla.crud_rapla_permission import get_permission_schema_by_id


def get_define_element_by_id(db: Session, element_id: int) -> Optional[RaplaDefineElement]:
    return db.query(RaplaDefineElement).filter(RaplaDefineElement.id == element_id).first()


def get_define_element_by_name(db: Session, name: str) -> Optional[RaplaDefineElement]:
    return db.query(RaplaDefineElement).filter(RaplaDefineElement.name == name).first()


def get_define_element_by_uuid(db: Session, uuid: str) -> Optional[RaplaDefineElement]:
    return db.query(RaplaDefineElement).filter(RaplaDefineElement.uuid == uuid).first()


def get_all_define_elements(db: Session,) -> List[RaplaDefineElement]:
    return db.query(RaplaDefineElement).order_by(RaplaDefineElement.name.asc()).all()


def create_define_element(db: Session, 
    name: str, 
    uuid: str | None = None,
    created_at: datetime | None = None,
    last_changed: datetime | None = None,
    last_changed_by: str | None = None,
) -> RaplaDefineElement:
  
    if uuid is not None:
        existing = get_define_element_by_uuid(db, uuid)
        if existing is not None:
            return existing
        
    now = datetime.now(timezone.utc)
    if created_at is None:
        created_at = now
    
    if last_changed is None:
        last_changed = created_at

    if uuid is None:
        uuid = str(uuid4())

    el = RaplaDefineElement(
        name=name, 
        uuid=uuid,
        created_at=created_at,
        last_changed=last_changed,
        last_changed_by=last_changed_by,
    )
    db.add(el)
    db.commit()
    db.refresh(el)
    return el




def delete_define_element(db: Session, element: RaplaDefineElement) -> None:
    db.delete(element)
    db.commit()


def get_define_element_full_schema(db: Session) -> list[DefineSchema]:
    model_define_elements = get_all_define_elements(db)
    defines: list[DefineSchema] = []

    for model_define_element in model_define_elements:
        schema_define_element =  get_define_element_full_schema_by_id(db, cast(int, model_define_element.id ))
        if schema_define_element is not None:
            raw_name = schema_define_element.name.split(":")[1]

            defines.append(DefineSchema(name=raw_name, element=schema_define_element))

    return defines

def get_define_element_full_schema_by_id(db: Session, element_id: int) -> DefineElementSchema | None:
    el = get_define_element_by_id(db, element_id)
    if el is None:
        return None

    # Names
    names: list[RaplaLanguageNameSchema] = []
    try:
        name_rows = list_language_names_for_define_element(db, element_id)
    except Exception:
        name_rows = []
    for nr in name_rows:
        s = get_language_name_schema_by_id(db, cast(int, nr.id))
        if s is not None:
            names.append(s)

    # Annotations
    ann_schemas: list[RaplaAnnotationSchema] = []
    try:
        ann_rels = list_annotation_relations(db, element_id)
    except Exception:
        ann_rels = []
    for ar in ann_rels:
        a = get_annotation_schema_by_id(db, cast(int, ar.id))
        if a is not None:
            ann_schemas.append(a)
    annotations_obj = RaplaAnnotationsSchema(annotations=ann_schemas) if ann_schemas else RaplaAnnotationsSchema()

    # Optionals (map relations -> optional ids -> full schemas)
    optionals:list[RaplaOptionalSchema] = []
    try:
        optional_rels = list_optional_relations_for_define_element(db, element_id)
    except Exception:
        optional_rels = []
    for orow in optional_rels:
        opt_schema = get_optional_element_full_schema_by_id(db, cast(int, orow.id) )
        if opt_schema is not None:
            optionals.append(RaplaOptionalSchema(opt_schema))
    
    # Permissions
    permissions: list[RaplaPermissionSchema] = []
    try:
        perm_rows = list_permissions_for_define_element(db, element_id)
    except Exception:
        perm_rows = []
    for pr in perm_rows:
        perm_schema = get_permission_schema_by_id(db, cast(int, pr.id))
        if perm_schema is not None:
            permissions.append(perm_schema)

    return DefineElementSchema(
        uuid = cast(str, el.uuid),
        name = cast(str, el.name),
        created_at = format_rapla_datetime(cast( datetime, el.created_at) ),
        last_changed = format_rapla_datetime(cast( datetime, el.last_changed) ),
        last_changed_by = cast(str, el.last_changed_by),
        names = names,
        annotations = annotations_obj,
        optionals = optionals,
        permissions = permissions,
    )
