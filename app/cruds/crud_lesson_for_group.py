from sqlalchemy.orm import Session

from app.models.model_lesson_for_group import LessonForGroup
from app.models.model_group import Group
from app.models.model_lessons import Lesson


def create_lesson_for_group_mapping(db: Session, lesson_id: int, group_id: int) -> LessonForGroup:
    existing = get_mapping_by_lesson_and_group(db, lesson_id, group_id)
    if existing is not None:
        return existing

    mapping = LessonForGroup(lesson_id=lesson_id, group_id=group_id)
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


def get_lesson_for_group_mappings(db: Session) -> list[LessonForGroup]:
    return db.query(LessonForGroup).order_by(LessonForGroup.id.asc()).all()


def get_lesson_for_group_mapping_by_id(db: Session, id: int) -> LessonForGroup | None:
    return db.query(LessonForGroup).filter(LessonForGroup.id == id).first()


def get_mapping_by_lesson_and_group(db: Session, lesson_id: int, group_id: int) -> LessonForGroup | None:
    return (
        db.query(LessonForGroup)
        .filter(LessonForGroup.lesson_id == lesson_id)
        .filter(LessonForGroup.group_id == group_id)
        .first()
    )


def get_groups_for_lesson(db: Session, lesson_id: int) -> list[Group]:
    return (
        db.query(Group)
        .join(LessonForGroup, Group.id == LessonForGroup.group_id)
        .filter(LessonForGroup.lesson_id == lesson_id)
        .order_by(Group.code.asc())
        .all()
    )


def get_lessons_for_group(db: Session, group_id: int) -> list[Lesson]:
    return (
        db.query(Lesson)
        .join(LessonForGroup, Lesson.id == LessonForGroup.lesson_id)
        .filter(LessonForGroup.group_id == group_id)
        .order_by(Lesson.date.asc(), Lesson.start_time.asc())
        .all()
    )


def delete_lesson_for_group_mapping(db: Session, lesson_id: int, group_id: int) -> bool:
    mapping = get_mapping_by_lesson_and_group(db, lesson_id, group_id)
    if mapping is None:
        return False

    db.delete(mapping)
    db.commit()
    return True
