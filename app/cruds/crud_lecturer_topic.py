from sqlalchemy.orm import Session, joinedload

from app.models.model_lecturer_topic import LecturerTopic
from app.models.model_thesis_proposal import ThesisProposal, ThesisProposalStatus


def create_lecturer_topic(
    db: Session,
    lecturer_id: int,
    topic: str,
    description: str | None,
) -> LecturerTopic:
    lecturer_topic = LecturerTopic(
        lecturer_id=lecturer_id,
        topic=topic.strip(),
        description=description.strip() if description else None,
    )
    db.add(lecturer_topic)
    db.commit()
    db.refresh(lecturer_topic)
    return lecturer_topic


def get_lecturer_topics_by_lecturer(db: Session, lecturer_id: int) -> list[LecturerTopic]:
    return (
        db.query(LecturerTopic)
        .options(joinedload(LecturerTopic.lecturer))
        .filter(LecturerTopic.lecturer_id == lecturer_id)
        .order_by(LecturerTopic.created_at.desc())
        .all()
    )


def get_available_lecturer_topics(db: Session) -> list[LecturerTopic]:
    return (
        db.query(LecturerTopic)
        .options(joinedload(LecturerTopic.lecturer))
        .filter(LecturerTopic.is_taken == False)  # noqa: E712
        .order_by(LecturerTopic.created_at.desc())
        .all()
    )


def get_lecturer_topic_by_id(db: Session, topic_id: int) -> LecturerTopic | None:
    return (
        db.query(LecturerTopic)
        .options(joinedload(LecturerTopic.lecturer))
        .filter(LecturerTopic.id == topic_id)
        .first()
    )


def delete_lecturer_topic(db: Session, topic_id: int, lecturer_id: int) -> bool:
    topic = (
        db.query(LecturerTopic)
        .filter(LecturerTopic.id == topic_id, LecturerTopic.lecturer_id == lecturer_id)
        .first()
    )
    if topic is None:
        return False
    if topic.is_taken:
        return False
    db.delete(topic)
    db.commit()
    return True


def mark_lecturer_topic_taken(db: Session, topic_id: int) -> None:
    topic = db.query(LecturerTopic).filter(LecturerTopic.id == topic_id).first()
    if topic:
        topic.is_taken = True
        db.add(topic)
        db.commit()


def count_own_proposals_for_student(db: Session, student_id: int) -> int:
    """Count non-rejected proposals where the student submitted their own topic (no lecturer_topic_id)."""
    return (
        db.query(ThesisProposal)
        .filter(
            ThesisProposal.student_id == student_id,
            ThesisProposal.lecturer_topic_id == None,  # noqa: E711
            ThesisProposal.status != ThesisProposalStatus.REJECTED,
        )
        .count()
    )


def count_selected_topics_for_student(db: Session, student_id: int) -> int:
    """Count non-rejected proposals where the student selected a lecturer-proposed topic."""
    return (
        db.query(ThesisProposal)
        .filter(
            ThesisProposal.student_id == student_id,
            ThesisProposal.lecturer_topic_id != None,  # noqa: E711
            ThesisProposal.status != ThesisProposalStatus.REJECTED,
        )
        .count()
    )


def get_all_lecturer_topics(db: Session) -> list[LecturerTopic]:
    return (
        db.query(LecturerTopic)
        .options(joinedload(LecturerTopic.lecturer))
        .order_by(LecturerTopic.created_at.desc())
        .all()
    )
