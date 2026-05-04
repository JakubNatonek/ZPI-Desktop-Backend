from datetime import datetime
from typing import cast

from sqlalchemy.orm import Session

from app.models.model_subject import Subject
from app.models.rapla.model_rapla_resourc import ModelRaplaResourc
from app.models.rapla.model_rapla_subject_to_resourc import RaplaSubjectToResourc
from app.schemas.rapla.resorces.schema_rapla_resourc_przedmiot import SchemaRaplaResourcPrzedmiot
from app.schemas.rapla.schema_rapla_permision import RaplaPermission as RaplaPermissionSchema
from app.cruds.rapla.crud_rapla_activity_to_category import get_categories_for_activity_id
from app.cruds.rapla.crud_rapla_permission_for_resourc import get_permission_by_resourc_id
from app.cruds.rapla.crud_rapla_permission import get_permission_schema_by_model
from app.cruds.rapla.rapla_format_datetime import format_rapla_datetime
from app.cruds.crud_department_for_field_of_study import get_departments_for_field_of_study
from app.cruds.crud_subject_for_field_of_study import get_primary_field_of_study_for_subject


def list_subject_to_resourc_mappings(db: Session) -> list[RaplaSubjectToResourc]:
    return db.query(RaplaSubjectToResourc).order_by(RaplaSubjectToResourc.id.asc()).all()


def get_resourc_by_subject_id(db: Session, subject_id: int) -> ModelRaplaResourc | None:
    mapping = (
        db.query(RaplaSubjectToResourc)
        .filter(RaplaSubjectToResourc.subject_id == subject_id)
        .first()
    )
    if mapping is None:
        return None

    return db.query(ModelRaplaResourc).filter(ModelRaplaResourc.id == mapping.rapla_resourc_id).first()


def get_subject_by_resourc_id(db: Session, rapla_resourc_id: int) -> Subject | None:
    mapping = (
        db.query(RaplaSubjectToResourc)
        .filter(RaplaSubjectToResourc.rapla_resourc_id == rapla_resourc_id)
        .first()
    )
    if mapping is None:
        return None

    return db.query(Subject).filter(Subject.id == mapping.subject_id).first()


def get_mapping_by_subject_and_resourc(db: Session, subject_id: int, rapla_resourc_id: int) -> RaplaSubjectToResourc | None:
    return (
        db.query(RaplaSubjectToResourc)
        .filter(RaplaSubjectToResourc.subject_id == subject_id)
        .filter(RaplaSubjectToResourc.rapla_resourc_id == rapla_resourc_id)
        .first()
    )


def create_subject_to_resourc_mapping(db: Session, subject_id: int, rapla_resourc_id: int) -> RaplaSubjectToResourc:
    existing = get_mapping_by_subject_and_resourc(db, subject_id, rapla_resourc_id)
    if existing is not None:
        return existing

    mapping = RaplaSubjectToResourc(subject_id=subject_id, rapla_resourc_id=rapla_resourc_id)
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


def delete_subject_to_resourc_mapping(db: Session, subject_id: int, rapla_resourc_id: int) -> bool:
    mapping = get_mapping_by_subject_and_resourc(db, subject_id, rapla_resourc_id)
    if mapping is None:
        return False

    db.delete(mapping)
    db.commit()
    return True


def _get_activity_category_key(db: Session, activity_id: int | None) -> str | None:
    if activity_id is None:
        return None

    categories = get_categories_for_activity_id(db, activity_id)
    if categories:
        return cast(str | None, getattr(categories[0], "key", None))

    return None


def subject_to_resourc_schema(db: Session, subject: Subject) -> SchemaRaplaResourcPrzedmiot | None:
    subject_id = cast(int | None, subject.id)
    if subject_id is None:
        return None

    resource = get_resourc_by_subject_id(db, subject_id)
    if resource is None:
        return None

    permission_models = get_permission_by_resourc_id(db, cast(int, resource.id)) or []
    permission_schemas: list[RaplaPermissionSchema] = []
    for permission_model in permission_models:
        permission_schema = get_permission_schema_by_model(db, permission_model)
        if permission_schema is not None:
            permission_schemas.append(permission_schema)

    primary_link = getattr(subject, "type_link", None)
    activity_id = cast(int | None, getattr(primary_link, "activity_id", None))
    activity_key = _get_activity_category_key(db, activity_id)

    field_of_study = get_primary_field_of_study_for_subject(db, subject_id)

    return SchemaRaplaResourcPrzedmiot(
        uuid=cast(str, resource.uuid),
        owner=cast(str, resource.owner),
        created_at=format_rapla_datetime(cast(datetime, resource.created_at)),
        last_changed=format_rapla_datetime(cast(datetime, resource.last_changed)),
        last_changed_by=cast(str, resource.last_changed_by),
        name=cast(str, subject.name),
        activity=activity_key,
        room_properties=cast(str | None, subject.room_properties),
        field_of_study_abbrevation=cast(str | None, getattr(field_of_study, "abbrevation", None)),
        field_of_study_year=cast(int | None, getattr(field_of_study, "year", None)),
        permissions=permission_schemas,
    )


def all_subject_to_resourc_schema(db: Session) -> list[SchemaRaplaResourcPrzedmiot]:
    subjects = db.query(Subject).order_by(Subject.name.asc(), Subject.id.asc()).all()
    schemas: list[SchemaRaplaResourcPrzedmiot] = []
    for subject in subjects:
        try:
            subject_schema = subject_to_resourc_schema(db, subject)
            if subject_schema is not None:
                schemas.append(subject_schema)
        except Exception:
            continue

    return schemas
