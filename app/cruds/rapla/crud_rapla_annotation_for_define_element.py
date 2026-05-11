from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_annotation_for_define_element import (
    RaplaAnnotationForDefineElement as RaplaAnnotationForDefineElementModel,
)
from app.models.rapla.model_rapla_annotation import RaplaAnnotation as RaplaAnnotationModel


def get_relation_by_id(db: Session, relation_id: int) -> Optional[RaplaAnnotationForDefineElementModel]:
    return db.query(RaplaAnnotationForDefineElementModel).filter(RaplaAnnotationForDefineElementModel.id == relation_id).first()


def get_relation(db: Session, annotation_id: int, define_element_id: int) -> Optional[RaplaAnnotationForDefineElementModel]:
    return (
        db.query(RaplaAnnotationForDefineElementModel)
        .filter(
            RaplaAnnotationForDefineElementModel.annotation_id == annotation_id,
            RaplaAnnotationForDefineElementModel.define_element_id == define_element_id,
        )
        .first()
    )


def list_relations(db: Session, skip: int = 0, limit: int = 100) -> List[RaplaAnnotationForDefineElementModel]:
    return db.query(RaplaAnnotationForDefineElementModel).offset(skip).limit(limit).all()


def list_relations_for_define_element(db: Session, define_element_id: int) -> List[RaplaAnnotationForDefineElementModel]:
    return (
        db.query(RaplaAnnotationForDefineElementModel)
        .filter(RaplaAnnotationForDefineElementModel.define_element_id == define_element_id)
        .all()
    )


def list_annotations_for_define_element(db: Session, define_element_id: int) -> List[RaplaAnnotationModel]:
    return (
        db.query(RaplaAnnotationModel)
        .join(
            RaplaAnnotationForDefineElementModel,
            RaplaAnnotationModel.id == RaplaAnnotationForDefineElementModel.annotation_id,
        )
        .filter(RaplaAnnotationForDefineElementModel.define_element_id == define_element_id)
        .order_by(RaplaAnnotationForDefineElementModel.id.asc())
        .all()
    )


def add_relation(db: Session, annotation_id: int, define_element_id: int) -> RaplaAnnotationForDefineElementModel:
    # Return existing relation if present
    existing = get_relation(db, annotation_id=annotation_id, define_element_id=define_element_id)
    if existing:
        return existing

    rel = RaplaAnnotationForDefineElementModel(annotation_id=annotation_id, define_element_id=define_element_id)
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


def remove_relation(db: Session, annotation_id: int, define_element_id: int) -> None:
    obj = get_relation(db, annotation_id=annotation_id, define_element_id=define_element_id)
    if not obj:
        return
    db.delete(obj)
    db.commit()
