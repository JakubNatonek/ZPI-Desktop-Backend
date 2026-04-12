from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.cruds.crud_admin_thesis import (
    admin_delete_proposal,
    admin_update_proposal_status,
    admin_update_proposal_topic,
    get_all_lecturers,
    get_all_proposals,
    get_proposal_by_id,
)
from app.cruds.crud_thesis_settings import get_or_create_thesis_settings, get_thesis_schedule_flags, update_thesis_settings
from app.models.model_thesis_proposal import ThesisProposal, ThesisProposalStatus
from app.models.model_thesis_settings import ThesisScheduleSettings
from app.models.model_user import User
from app.dependencies.auth import require_role
from app.schemas.admin_thesis import (
    AdminThesisProposalResponse,
    AdminThesisSettingsResponse,
    AdminThesisSettingsUpdate,
    AdminThesisStats,
    AdminThesisStatusUpdate,
    AdminThesisTopicUpdate,
)
from app.schemas.thesis import LecturerResponse

router = APIRouter(prefix="/thesis", tags=["admin-thesis"])


# def _require_admin(current_user: User = Depends(get_current_user)) -> User:
#     role_value = current_user.role.name if current_user.role else str(current_user.role)
#     if role_value != "admin":
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
#     return current_user


def _to_admin_response(proposal: ThesisProposal) -> AdminThesisProposalResponse:
    student_name = ""
    student_email = ""
    student_index = None
    student_group = None
    lecturer_name = ""
    lecturer_email = ""

    if proposal.student:
        student_name = f"{proposal.student.first_name} {proposal.student.last_name}".strip()
        student_email = proposal.student.email or ""
        if hasattr(proposal.student, "student_profile") and proposal.student.student_profile:
            student_index = proposal.student.student_profile.index_number
            if proposal.student.student_profile.group:
                g = proposal.student.student_profile.group
                student_group = f"{g.specialization} {g.code}"

    if proposal.lecturer:
        lecturer_name = f"{proposal.lecturer.first_name} {proposal.lecturer.last_name}".strip()
        lecturer_email = proposal.lecturer.email or ""

    return AdminThesisProposalResponse(
        id=proposal.id,
        student_id=proposal.student_id,
        student_name=student_name,
        student_email=student_email,
        student_index=student_index,
        student_group=student_group,
        student_average_grade=proposal.student_average_grade,
        lecturer_id=proposal.lecturer_id,
        lecturer_name=lecturer_name,
        lecturer_email=lecturer_email,
        topic=proposal.topic,
        justification=proposal.justification,
        status=proposal.status.value,
        submitted_at=proposal.submitted_at,
        reviewed_at=proposal.reviewed_at,
    )


def _to_settings_response(settings: ThesisScheduleSettings) -> AdminThesisSettingsResponse:
    flags = get_thesis_schedule_flags(settings)
    return AdminThesisSettingsResponse(
        tab_visible_from=settings.tab_visible_from,
        tab_visible_to=settings.tab_visible_to,
        topic_submission_from=settings.topic_submission_from,
        topic_submission_to=settings.topic_submission_to,
        proposal_selection_from=settings.proposal_selection_from,
        proposal_selection_deadline=settings.proposal_selection_deadline,
        tab_visible_now=flags["tab_visible_now"],
        topic_submission_open=flags["topic_submission_open"],
        proposal_selection_open=flags["proposal_selection_open"],
        updated_at=settings.updated_at,
    )


@router.get(
    "/settings",
    response_model=AdminThesisSettingsResponse,
    summary="Pobierz ustawienia dat prac dyplomowych",
)
def get_settings(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> AdminThesisSettingsResponse:
    settings = get_or_create_thesis_settings(db)
    return _to_settings_response(settings)


@router.patch(
    "/settings",
    response_model=AdminThesisSettingsResponse,
    summary="Zaktualizuj ustawienia dat prac dyplomowych",
)
def patch_settings(
    payload: AdminThesisSettingsUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> AdminThesisSettingsResponse:
    settings = update_thesis_settings(
        db,
        tab_visible_from=payload.tab_visible_from,
        tab_visible_to=payload.tab_visible_to,
        topic_submission_from=payload.topic_submission_from,
        topic_submission_to=payload.topic_submission_to,
        proposal_selection_from=payload.proposal_selection_from,
        proposal_selection_deadline=payload.proposal_selection_deadline,
    )
    return _to_settings_response(settings)


@router.get(
    "/proposals",
    response_model=list[AdminThesisProposalResponse],
    summary="Lista wszystkich propozycji prac dyplomowych",
)
def list_all_proposals(
    status_filter: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> list[AdminThesisProposalResponse]:
    thesis_status = None
    if status_filter:
        try:
            thesis_status = ThesisProposalStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}",
            )
    proposals = get_all_proposals(db, status_filter=thesis_status)
    return [_to_admin_response(p) for p in proposals]


@router.get(
    "/proposals/stats",
    response_model=AdminThesisStats,
    summary="Statystyki propozycji prac dyplomowych",
)
def get_proposal_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> AdminThesisStats:
    all_proposals = get_all_proposals(db)
    return AdminThesisStats(
        total=len(all_proposals),
        pending=sum(1 for p in all_proposals if p.status == ThesisProposalStatus.PENDING),
        approved=sum(1 for p in all_proposals if p.status == ThesisProposalStatus.APPROVED),
        rejected=sum(1 for p in all_proposals if p.status == ThesisProposalStatus.REJECTED),
    )


@router.get(
    "/proposals/{proposal_id}",
    response_model=AdminThesisProposalResponse,
    summary="Szczegóły propozycji pracy dyplomowej",
)
def get_proposal_detail(
    proposal_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> AdminThesisProposalResponse:
    proposal = get_proposal_by_id(db, proposal_id)
    if proposal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    return _to_admin_response(proposal)


@router.patch(
    "/proposals/{proposal_id}/status",
    response_model=AdminThesisProposalResponse,
    summary="Zmiana statusu propozycji (zatwierdzenie/odrzucenie)",
)
def update_proposal_status(
    proposal_id: int,
    payload: AdminThesisStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> AdminThesisProposalResponse:
    proposal = admin_update_proposal_status(
        db,
        proposal_id=proposal_id,
        new_status=ThesisProposalStatus(payload.status.value),
    )
    if proposal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    return _to_admin_response(proposal)


@router.patch(
    "/proposals/{proposal_id}/topic",
    response_model=AdminThesisProposalResponse,
    summary="Edycja tematu pracy dyplomowej",
)
def update_proposal_topic(
    proposal_id: int,
    payload: AdminThesisTopicUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> AdminThesisProposalResponse:
    proposal = admin_update_proposal_topic(
        db,
        proposal_id=proposal_id,
        topic=payload.topic,
    )
    if proposal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    return _to_admin_response(proposal)


@router.delete(
    "/proposals/{proposal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Usunięcie propozycji pracy dyplomowej",
)
def delete_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> None:
    deleted = admin_delete_proposal(db, proposal_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")


@router.get(
    "/lecturers",
    response_model=list[LecturerResponse],
    summary="Lista promotorów (dla admina)",
)
def list_lecturers(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> list[LecturerResponse]:
    lecturers = get_all_lecturers(db)
    return [
        LecturerResponse(
            user_id=l.user_id,
            first_name=l.first_name,
            last_name=l.last_name,
            email=l.email,
        )
        for l in lecturers
    ]
