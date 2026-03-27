from typing import List, Optional, cast
from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_annotation import RaplaAnnotation as RaplaAnnotationModel
from app.schemas.rapla.schema_rapla_annotation import RaplaAnnotation as RaplaAnnotationSchema


def get_annotation(db: Session, annotation_id: int) -> Optional[RaplaAnnotationModel]:
    return db.query(RaplaAnnotationModel).filter(RaplaAnnotationModel.id == annotation_id).first()


def get_annotation_by_key(db: Session, key: str) -> Optional[RaplaAnnotationModel]:
    return db.query(RaplaAnnotationModel).filter(RaplaAnnotationModel.key == key).first()


def list_annotations(db: Session, skip: int = 0, limit: int = 100) -> List[RaplaAnnotationModel]:
    return db.query(RaplaAnnotationModel).offset(skip).limit(limit).all()


def create_annotation(
    db: Session,
    *,
    key: str,
    value: Optional[str] = None,
) -> RaplaAnnotationModel:
    db_obj = RaplaAnnotationModel(
        key=key, value=value
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_annotation(
    db: Session,
    db_obj: RaplaAnnotationModel,
    *,
    key: Optional[str] = None,
    value: Optional[str] = None
) -> RaplaAnnotationModel:
    if key is not None:
        db_obj.key = key
    if value is not None:
        db_obj.value = value

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_annotation_by_id(db: Session, annotation_id: int) -> None:
    obj = get_annotation(db, annotation_id)
    if not obj:
        return
    db.delete(obj)
    db.commit()


def get_annotation_schema_by_id(db: Session, annotation_id: int) -> Optional[RaplaAnnotationSchema]:
    obj = get_annotation(db, annotation_id)
    if not obj:
        return None
    return RaplaAnnotationSchema(key = cast( str, obj.key ), value = cast( str, obj.value ))
