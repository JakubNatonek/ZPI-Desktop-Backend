from sqlalchemy.orm import Session, joinedload, subqueryload

from app.core.thesis_datetime import utc_now_minute
from app.models.model_thesis_proposal import ThesisProposal, ThesisProposalStatus
from app.models.model_user import User


def get_all_proposals(
    db: Session,
    status_filter: ThesisProposalStatus | None = None,
) -> list[ThesisProposal]:
    query = db.query(ThesisProposal).options(
        joinedload(ThesisProposal.student),
        joinedload(ThesisProposal.lecturer),
    )
    if status_filter is not None:
        query = query.filter(ThesisProposal.status == status_filter)
    return (
        query
        .order_by(ThesisProposal.submitted_at.desc())
        .all()
    )


def get_proposal_by_id(db: Session, proposal_id: int) -> ThesisProposal | None:
    return (
        db.query(ThesisProposal)
        .options(
            joinedload(ThesisProposal.student),
            joinedload(ThesisProposal.lecturer),
        )
        .filter(ThesisProposal.id == proposal_id)
        .first()
    )


def admin_update_proposal_status(
    db: Session,
    proposal_id: int,
    new_status: ThesisProposalStatus,
) -> ThesisProposal | None:
    proposal = get_proposal_by_id(db, proposal_id)
    if proposal is None:
        return None

    proposal.status = new_status
    proposal.reviewed_at = utc_now_minute()
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


def admin_update_proposal_topic(
    db: Session,
    proposal_id: int,
    topic: str,
) -> ThesisProposal | None:
    proposal = get_proposal_by_id(db, proposal_id)
    if proposal is None:
        return None

    proposal.topic = topic.strip()
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


def admin_delete_proposal(db: Session, proposal_id: int) -> bool:
    proposal = db.query(ThesisProposal).filter(ThesisProposal.id == proposal_id).first()
    if proposal is None:
        return False

    db.delete(proposal)
    db.commit()
    return True


def get_all_lecturers(db: Session) -> list[User]:
    from app.cruds.crud_thesis import get_lecturers
    return get_lecturers(db)


def get_approved_proposals_for_print(
    db: Session,
    department_id: int,
    studies_type: str | None = None,
) -> list[ThesisProposal]:
    from app.models.model_student import Student
    from app.models.model_group import Group

    query = (
        db.query(ThesisProposal)
        .join(User, ThesisProposal.student_id == User.user_id)
        .join(Student, Student.user_id == User.user_id)
        .join(Group, Student.group_id == Group.id)
        .filter(
            ThesisProposal.status == ThesisProposalStatus.APPROVED,
            Group.department_id == department_id,
        )
        .options(
            joinedload(ThesisProposal.student),
            joinedload(ThesisProposal.lecturer),
            joinedload(ThesisProposal.lecturer_topic),
        )
    )

    if studies_type:
        from sqlalchemy import func
        query = query.filter(func.lower(Group.studies_type) == studies_type.strip().lower())

    return query.order_by(ThesisProposal.submitted_at.asc()).all()
