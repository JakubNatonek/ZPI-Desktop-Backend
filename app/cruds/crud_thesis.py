from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.text_normalization import normalize_lookup_value
from app.models.model_thesis_proposal import ThesisProposal, ThesisProposalStatus
from app.models.model_user import User
from app.models.model_role import Role

# NOTE: just do a table nex time
LECTURER_ROLE_NAMES = {"lecturer", "wykladowca", "cwiczenia", "laboratorium", "seminarium"}


def _is_lecturer_user(user: User) -> bool:
    role_name = normalize_lookup_value(user.role.name if user.role else "")
    return role_name in LECTURER_ROLE_NAMES


# NOTE this all need a redo
def get_lecturers(db: Session) -> list[User]:
    users = (
        db.query(User)
        .join(Role, Role.id == User.role_id)
        .order_by(User.last_name.asc(), User.first_name.asc())
        .all()
    )
    return [user for user in users if _is_lecturer_user(user)]


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
    if not _is_lecturer_user(lecturer):
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
    proposal.reviewed_at = datetime.now(timezone.utc)
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal
