from typing import List, Optional, cast
from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_optional_element import RaplaOptionalElement
from app.schemas.rapla.schema_rapla_language_name import RaplaLanguageName as RaplaLanguageNameSchema
from app.schemas.rapla.schema_rapla_constraint import RaplaConstraint as RaplaConstraintSchema
from app.schemas.rapla.schema_rapla_annotation import RaplaAnnotation as RaplaAnnotationSchema
from app.schemas.rapla.schema_rapla_annotations import RaplaAnnotations as RaplaAnnotationsSchema
from app.schemas.rapla.schema_rapla_data_type import RaplaDataType as RaplaDataTypeSchema
from app.schemas.rapla.schema_rapla_optional_element import OptionalElement as OptionalElementSchema

# helper cruds
from app.cruds.rapla.crud_rapla_data_type_for_optional_element import get_data_type_for_optional_element
from app.cruds.rapla.crud_rapla_data_type import get_data_type_schema_by_id
from app.cruds.rapla.crud_rapla_language_name_for_optional_element import list_language_names_for_optional_element
from app.cruds.rapla.crud_rapla_language_name import get_language_name_schema_by_id
from app.cruds.rapla.crud_rapla_constraint_for_optional_element import list_constraints_for_optional_element
from app.cruds.rapla.crud_rapla_constraint import get_constraint_schema_by_id
from app.cruds.rapla.crud_rapla_annotation_for_optional_element import list_relations_for_optional_element as list_annotation_relations
from app.cruds.rapla.crud_rapla_annotation import get_annotation_schema_by_id



def get_optional_element_by_id(db: Session, element_id: int) -> Optional[RaplaOptionalElement]:
    return db.query(RaplaOptionalElement).filter(RaplaOptionalElement.id == element_id).first()


def get_optional_element_by_name(db: Session, name: str) -> Optional[RaplaOptionalElement]:
    return db.query(RaplaOptionalElement).filter(RaplaOptionalElement.name == name).first()


def list_optional_elements(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[RaplaOptionalElement]:
    q = db.query(RaplaOptionalElement).order_by(RaplaOptionalElement.name.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def create_optional_element(db: Session, name: str, default_value: Optional[str] = None) -> RaplaOptionalElement:
    existing = get_optional_element_by_name(db, name)
    if existing:
        return existing

    el = RaplaOptionalElement(name=name, default_value=default_value)
    db.add(el)
    db.commit()
    db.refresh(el)
    return el

# WTF IS THIS NEED I HELP
def update_optional_element(db: Session, element: RaplaOptionalElement, **fields) -> RaplaOptionalElement:
    for k, v in fields.items():
        if hasattr(element, k):
            setattr(element, k, v)
    db.add(element)
    db.commit()
    db.refresh(element)
    return element


def delete_optional_element(db: Session, element: RaplaOptionalElement) -> None:
    db.delete(element)
    db.commit()


def get_optional_element_full_schema_by_id(db: Session, element_id: int) -> Optional[OptionalElementSchema]:
    el = get_optional_element_by_id(db, element_id)
    if el is None:
        return None

    # Names
    names: list[RaplaLanguageNameSchema] = []
    lang_names = list_language_names_for_optional_element(db, element_id)

    for lang_name in lang_names:
        name =  get_language_name_schema_by_id(db, cast( int, lang_name.id ) ) 
        if name is not None:
            names.append(name)

    # Constraints
    constraints: list[RaplaConstraintSchema] = []
    constraint_rows = list_constraints_for_optional_element(db, element_id)
    for cr in constraint_rows:
        cs = get_constraint_schema_by_id(db, cast( int, cr.id ) )
        if cs is not None:
            constraints.append(cs)

    # Annotations
    ann_schemas: list[RaplaAnnotationSchema] = []

    try:
        ann_rels = list_annotation_relations(db, element_id)
    except Exception:
        ann_rels = []
    for ar in ann_rels:
        ann_id = getattr(ar, "annotation_id", None)
        if ann_id is None:
            continue
        a = get_annotation_schema_by_id(db, ann_id)
        if a is not None:
            ann_schemas.append(a)

    annotations_obj = RaplaAnnotationsSchema(annotations=ann_schemas) if ann_schemas else None

    # Data type schema: fetch mapped data-type row safely and convert to schema
    dt_schema: Optional[RaplaDataTypeSchema] = None
    dt_model = get_data_type_for_optional_element(db, element_id)
    if dt_model is not None:
        dt_schema = get_data_type_schema_by_id(db, cast(int, dt_model.id))


    schema_optional_element = OptionalElementSchema(
        name=cast(str, el.name),
        data_type=dt_schema or RaplaDataTypeSchema(""),
        default_value=cast(Optional[str], el.default_value),
        names=names,
        constraints=constraints or None,
        annotations=annotations_obj or None,
    )

    return schema_optional_element