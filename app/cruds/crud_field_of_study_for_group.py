
from sqlalchemy.orm import Session

from app.models.model_field_of_study_for_group import ModelFieldOfStudyForGroup
from app.models.model_group import Group
from app.models.model_field_of_study import FieldOfStudy

from app.cruds.crud_field_of_study import get_field_of_study_by_id



def create_field_of_study_for_group_maping(db: Session, id_field_of_study: int, id_group: int) -> ModelFieldOfStudyForGroup:
    mapping = (
        db.query(ModelFieldOfStudyForGroup)
        .filter(ModelFieldOfStudyForGroup.field_of_study_id == id_field_of_study)
        .filter(ModelFieldOfStudyForGroup.group_id == id_group)
        .first()
    )
    if mapping is not None:
        return mapping

    mapping = ModelFieldOfStudyForGroup(field_of_study_id=id_field_of_study, group_id=id_group)
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


def get_field_of_study_for_group_maping(db: Session) -> list[ModelFieldOfStudyForGroup]:
    return db.query(ModelFieldOfStudyForGroup).all()

def get_field_of_study_for_group_maping_by_id(db: Session, id:int) -> ModelFieldOfStudyForGroup | None:
    return db.query(ModelFieldOfStudyForGroup).filter(ModelFieldOfStudyForGroup.id == id).first()

def get_group_from_maping_by_id(db: Session, id:int) -> Group | None:
    from app.cruds.crud_group import get_group_by_id
    maping = get_field_of_study_for_group_maping_by_id(db, id)

    return get_group_by_id(db, maping.group_id)

def get_field_of_study_from_maping_by_id(db: Session, id:int) -> FieldOfStudy | None:
    maping = get_field_of_study_for_group_maping_by_id(db, id)

    return get_field_of_study_by_id(db, maping.field_of_study_id)

def get_field_of_study_from_maping_by_group_id(db: Session, id_group:int) -> FieldOfStudy | None:
    maping =  db.query(ModelFieldOfStudyForGroup).filter(ModelFieldOfStudyForGroup.group_id == id_group).first()

    return get_field_of_study_by_id(db, maping.field_of_study_id)

def get_groups_from_maping_by_field_of_study_id(
    db: Session,
    id_field_of_study: int
) -> list[Group]:
    from app.cruds.crud_group import get_group_by_id
    mapings = (
        db.query(ModelFieldOfStudyForGroup)
        .filter(ModelFieldOfStudyForGroup.field_of_study_id == id_field_of_study)
        .all()
    )

    return [
        group
        for mapping in mapings
        if (group := get_group_by_id(db, mapping.group_id)) is not None
    ]