from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.cruds.crud_thesis import (
    count_approved_for_lecturer,
    create_thesis_proposal,
    get_lecturers,
    get_proposals_for_lecturer,
    update_proposal_status,
)
from app.models.model_thesis_proposal import ThesisProposal, ThesisProposalStatus
from app.models.model_user import User
from app.schemas.thesis import (
    LecturerResponse,
    ThesisProposalCreateRequest,
    ThesisProposalResponse,
    ThesisProposalStatusUpdateRequest,
)


router = APIRouter(prefix="/thesis", tags=["thesis"])

MAX_APPROVED_PROPOSALS = 3
LECTURER_ROLE_NAMES = {"lecturer", "wykladowca", "cwiczenia", "laboratorium", "seminarium"}
STUDENT_ROLE_NAMES = {"student"}


def _is_lecturer(user: User) -> bool:
    role_name = (user.role.name if user.role else "").strip().lower()
    return role_name in LECTURER_ROLE_NAMES


def _is_student(user: User) -> bool:
    role_name = (user.role.name if user.role else "").strip().lower()
    return role_name in STUDENT_ROLE_NAMES


def _to_response(proposal: ThesisProposal) -> ThesisProposalResponse:
    student_name = ""
    lecturer_name = ""

    if proposal.student:
        student_name = f"{proposal.student.first_name} {proposal.student.last_name}".strip()

    if proposal.lecturer:
        lecturer_name = f"{proposal.lecturer.first_name} {proposal.lecturer.last_name}".strip()

    return ThesisProposalResponse(
        id=proposal.id,
        student_id=proposal.student_id,
        student_name=student_name,
        student_email=proposal.student.email if proposal.student else "",
        student_average_grade=proposal.student_average_grade,
        lecturer_id=proposal.lecturer_id,
        lecturer_name=lecturer_name,
        topic=proposal.topic,
        justification=proposal.justification,
        status=proposal.status.value,
        submitted_at=proposal.submitted_at,
        reviewed_at=proposal.reviewed_at,
    )


@router.get("/lecturers", response_model=list[LecturerResponse], summary="List lecturers")
def list_lecturers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LecturerResponse]:
    if not _is_student(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can list lecturers")

    lecturers = get_lecturers(db)
    return [
        LecturerResponse(
            user_id=lecturer.user_id,
            first_name=lecturer.first_name,
            last_name=lecturer.last_name,
            email=lecturer.email,
        )
        for lecturer in lecturers
    ]


@router.post("/proposals", response_model=ThesisProposalResponse, status_code=201, summary="Submit thesis proposal")
def submit_proposal(
    payload: ThesisProposalCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ThesisProposalResponse:
    if not _is_student(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can submit proposals")

    try:
        proposal = create_thesis_proposal(
            db,
            student_id=current_user.user_id,
            lecturer_id=payload.lecturer_id,
            topic=payload.topic,
            justification=payload.justification,
            student_average_grade=payload.student_average_grade,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return _to_response(proposal)


@router.get("/proposals", response_model=list[ThesisProposalResponse], summary="List lecturer thesis proposals")
def list_lecturer_proposals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ThesisProposalResponse]:
    if not _is_lecturer(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can view proposals")

    proposals = get_proposals_for_lecturer(db, current_user.user_id)
    return [_to_response(proposal) for proposal in proposals]


@router.patch(
    "/proposals/{proposal_id}/status",
    response_model=ThesisProposalResponse,
    summary="Approve or reject thesis proposal",
)
def review_proposal(
    proposal_id: int,
    payload: ThesisProposalStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ThesisProposalResponse:
    if not _is_lecturer(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can review proposals")

    if payload.status == ThesisProposalStatus.APPROVED:
        approved_count = count_approved_for_lecturer(db, current_user.user_id)
        if approved_count >= MAX_APPROVED_PROPOSALS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum approved proposals reached ({MAX_APPROVED_PROPOSALS})",
            )

    try:
        proposal = update_proposal_status(
            db,
            proposal_id=proposal_id,
            lecturer_id=current_user.user_id,
            status=ThesisProposalStatus(payload.status.value),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if proposal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")

    return _to_response(proposal)
