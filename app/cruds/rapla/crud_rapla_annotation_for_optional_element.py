from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.rapla.model_rapla_annotation_for_optional_element import (
    RaplaAnnotationForOptionalElement as RaplaAnnotationForOptionalElementModel,
)
from app.models.rapla.model_rapla_annotation import RaplaAnnotation as RaplaAnnotationModel
from app.models.rapla.model_rapla_optional_element import RaplaOptionalElement as RaplaOptionalElementModel


def get_relation_by_id(db: Session, relation_id: int) -> Optional[RaplaAnnotationForOptionalElementModel]:
    return db.query(RaplaAnnotationForOptionalElementModel).filter(RaplaAnnotationForOptionalElementModel.id == relation_id).first()


def get_relation(db: Session, annotation_id: int, optional_element_id: int) -> Optional[RaplaAnnotationForOptionalElementModel]:
    return (
        db.query(RaplaAnnotationForOptionalElementModel)
        .filter(
            RaplaAnnotationForOptionalElementModel.annotation_id == annotation_id,
            RaplaAnnotationForOptionalElementModel.optional_element_id == optional_element_id,
        )
        .first()
    )


def list_relations(db: Session, skip: int = 0, limit: int = 100) -> List[RaplaAnnotationForOptionalElementModel]:
    return db.query(RaplaAnnotationForOptionalElementModel).offset(skip).limit(limit).all()


def list_relations_for_optional_element(db: Session, optional_element_id: int) -> List[RaplaAnnotationForOptionalElementModel]:
    return (
        db.query(RaplaAnnotationForOptionalElementModel)
        .filter(RaplaAnnotationForOptionalElementModel.optional_element_id == optional_element_id)
        .all()
    )


def list_annotations_for_optional_element(db: Session, optional_element_id: int) -> List[RaplaAnnotationModel]:
    return (
        db.query(RaplaAnnotationModel)
        .join(
            RaplaAnnotationForOptionalElementModel,
            RaplaAnnotationModel.id == RaplaAnnotationForOptionalElementModel.annotation_id,
        )
        .filter(RaplaAnnotationForOptionalElementModel.optional_element_id == optional_element_id)
        .order_by(RaplaAnnotationForOptionalElementModel.id.asc())
        .all()
    )


def add_relation(db: Session, annotation_id: int, optional_element_id: int) -> RaplaAnnotationForOptionalElementModel:
    existing = get_relation(db, annotation_id=annotation_id, optional_element_id=optional_element_id)
    if existing:
        return existing

    rel = RaplaAnnotationForOptionalElementModel(annotation_id=annotation_id, optional_element_id=optional_element_id)
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


def remove_relation_by_id(db: Session, relation_id: int) -> None:
    obj = get_relation_by_id(db, relation_id)
    if not obj:
        return
    db.delete(obj)
    db.commit()


def remove_relation(db: Session, annotation_id: int, optional_element_id: int) -> None:
    obj = get_relation(db, annotation_id=annotation_id, optional_element_id=optional_element_id)
    if not obj:
        return
    db.delete(obj)
    db.commit()
