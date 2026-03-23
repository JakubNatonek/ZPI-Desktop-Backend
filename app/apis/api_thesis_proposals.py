from typing import List
import unicodedata

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.models.model_thesis_proposal import ThesisProposal
from app.models.model_user import User
from app.schemas.thesis_proposal import (
    SubmitThesisProposalPayload,
    ThesisLecturerItem,
    ThesisProposalResponse,
    UpdateThesisProposalStatusPayload,
)

router = APIRouter(prefix="/thesis-proposals", tags=["thesis-proposals"])


def _is_teacher(user: User) -> bool:
    role_name = (user.role.name if user.role else "").strip().lower()
    role_name = role_name.replace(chr(322), "l")
    role_name = unicodedata.normalize("NFKD", role_name).encode("ascii", "ignore").decode("ascii")
    return role_name in {"wykladowca", "wykadowca", "teacher", "lecturer"} or user.teacher_profile is not None


def _to_response(item: ThesisProposal) -> ThesisProposalResponse:
    status = "PENDING"
    if item.is_reviewed:
        status = "APPROVED" if item.is_approved else "REJECTED"

    lecturer_name = ""
    if item.lecturer is not None:
        lecturer_name = f"{item.lecturer.first_name} {item.lecturer.last_name}".strip()

    return ThesisProposalResponse(
        id=item.id,
        studentName=item.student_name,
        studentEmail=item.student_email,
        studentAverageGrade=item.student_average_grade,
        lecturerId=item.lecturer_user_id,
        lecturerName=lecturer_name,
        topic=item.topic,
        justification=item.justification,
        status=status,
        submittedAt=item.submitted_at,
    )


@router.get("/lecturers", response_model=List[ThesisLecturerItem], summary="Get lecturers")
def get_lecturers(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> List[ThesisLecturerItem]:
    users = db.query(User).all()

    return [
        ThesisLecturerItem(
            id=user.user_id,
            firstName=user.first_name,
            lastName=user.last_name,
            email=user.email,
        )
        for user in users
        if _is_teacher(user)
    ]


@router.get("", response_model=List[ThesisProposalResponse], summary="Get thesis proposals")
def get_proposals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ThesisProposalResponse]:
    query = db.query(ThesisProposal)

    if _is_teacher(current_user):
        query = query.filter(ThesisProposal.lecturer_user_id == current_user.user_id)
    else:
        query = query.filter(ThesisProposal.student_user_id == current_user.user_id)

    proposals = query.order_by(ThesisProposal.student_average_grade.desc(), ThesisProposal.submitted_at.desc()).all()
    return [_to_response(item) for item in proposals]


@router.post("", response_model=ThesisProposalResponse, summary="Submit thesis proposal")
def submit_proposal(
    payload: SubmitThesisProposalPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ThesisProposalResponse:
    if _is_teacher(current_user):
        raise HTTPException(status_code=403, detail="Only students can submit thesis proposals")

    lecturer = db.query(User).filter(User.user_id == payload.lecturerId).first()
    if lecturer is None or not _is_teacher(lecturer):
        raise HTTPException(status_code=400, detail="Invalid lecturerId")

    proposal = ThesisProposal(
        topic=payload.topic,
        justification=payload.justification,
        student_name=f"{current_user.first_name} {current_user.last_name}".strip(),
        student_email=current_user.email,
        student_average_grade=payload.studentAverageGrade,
        lecturer_user_id=lecturer.user_id,
        student_user_id=current_user.user_id,
        is_reviewed=False,
        is_approved=False,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    return _to_response(proposal)


@router.patch("/{proposal_id}/status", response_model=ThesisProposalResponse, summary="Update thesis proposal status")
def update_status(
    proposal_id: int,
    payload: UpdateThesisProposalStatusPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ThesisProposalResponse:
    if not _is_teacher(current_user):
        raise HTTPException(status_code=403, detail="Only teachers can update proposal status")

    proposal = db.query(ThesisProposal).filter(ThesisProposal.id == proposal_id).first()
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if proposal.lecturer_user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Proposal is not assigned to current teacher")

    proposal.is_reviewed = True
    proposal.is_approved = payload.isApproved

    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    return _to_response(proposal)
