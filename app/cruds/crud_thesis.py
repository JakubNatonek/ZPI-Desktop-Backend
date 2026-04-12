from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.thesis_datetime import utc_now_minute
from app.cruds.crud_roles_for_user import get_roles_for_user
from app.models.model_thesis_proposal import ThesisProposal, ThesisProposalStatus
from app.models.model_user import User

def _is_lecturer_user(db: Session, user_id: int) -> bool:
    role_names = {
        str(role.name).strip().lower()
        for role in get_roles_for_user(db, user_id)
        if role.name
    }
    return "wykladowca" in role_names


# NOTE this all need a redo
def get_lecturers(db: Session) -> list[User]:
    users = db.query(User).order_by(User.last_name.asc(), User.first_name.asc()).all()
    lecturers = []

    for user in users:
        if _is_lecturer_user(db, user.user_id):
            lecturers.append(user)

    return lecturers


def create_thesis_proposal(
    db: Session,
    student_id: int,
    lecturer_id: int,
    topic: str,
    justification: str,
    student_average_grade: float,
) -> ThesisProposal:
    lecturer = db.query(User).filter(User.user_id == lecturer_id).first()
    if lecturer is None:
        raise ValueError("Selected lecturer does not exist")
    if not _is_lecturer_user(db, lecturer.user_id):
        raise ValueError("Selected user is not a lecturer")

    proposal = ThesisProposal(
        student_id=student_id,
        lecturer_id=lecturer_id,
        student_average_grade=student_average_grade,
        topic=topic.strip(),
        justification=justification.strip(),
        status=ThesisProposalStatus.PENDING,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


def get_proposals_for_lecturer(db: Session, lecturer_id: int) -> list[ThesisProposal]:
    return (
        db.query(ThesisProposal)
        .filter(ThesisProposal.lecturer_id == lecturer_id)
        .order_by(ThesisProposal.student_average_grade.desc(), ThesisProposal.submitted_at.desc())
        .all()
    )


def count_approved_for_lecturer(db: Session, lecturer_id: int) -> int:
    return (
        db.query(ThesisProposal)
        .filter(
            ThesisProposal.lecturer_id == lecturer_id,
            ThesisProposal.status == ThesisProposalStatus.APPROVED,
        )
        .count()
    )


def update_proposal_status(
    db: Session,
    proposal_id: int,
    lecturer_id: int,
    status: ThesisProposalStatus,
) -> ThesisProposal | None:
    proposal = (
        db.query(ThesisProposal)
        .filter(
            ThesisProposal.id == proposal_id,
            ThesisProposal.lecturer_id == lecturer_id,
        )
        .first()
    )
    if proposal is None:
        return None

    if proposal.status != ThesisProposalStatus.PENDING:
        raise ValueError("Only pending proposals can be reviewed")

    proposal.status = status
    proposal.reviewed_at = utc_now_minute()
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal
