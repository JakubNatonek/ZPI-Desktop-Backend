from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

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
    proposal.reviewed_at = datetime.now(timezone.utc)
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
