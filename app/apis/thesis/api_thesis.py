from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user, user_has_role
from app.core.database import get_db
from app.cruds.crud_admin_thesis import admin_update_proposal_status, get_all_proposals
from app.cruds.crud_lecturer_topic import (
    count_own_proposals_for_student,
    count_selected_topics_for_student,
    create_lecturer_topic,
    delete_lecturer_topic,
    get_available_lecturer_topics,
    get_lecturer_topic_by_id,
    get_lecturer_topics_by_lecturer,
    mark_lecturer_topic_taken,
)
from app.cruds.crud_thesis import (
    count_approved_for_lecturer,
    create_thesis_proposal,
    get_lecturers,
    get_proposals_for_lecturer,
    get_proposals_for_student,
    get_student_average_grade,
    update_proposal_status,
    withdraw_proposal,
)
from app.cruds.crud_thesis_settings import get_or_create_thesis_settings, get_thesis_schedule_flags
from app.dependencies.auth import require_role
from app.models.model_lecturer_topic import LecturerTopic
from app.models.model_thesis_proposal import ThesisProposal, ThesisProposalStatus
from app.models.model_user import User
from app.schemas.lecturer_topic import LecturerTopicCreateRequest, LecturerTopicResponse
from app.schemas.thesis import (
    LecturerResponse,
    ThesisProposalCreateRequest,
    ThesisProposalResponse,
    ThesisScheduleAvailabilityResponse,
    ThesisProposalStatusUpdateRequest,
)


router = APIRouter(prefix="/thesis", tags=["thesis"])


def _is_admin(user: User) -> bool:
    return user_has_role(user, "admin")


def _to_response(proposal: ThesisProposal, db: Session) -> ThesisProposalResponse:
    student_name = ""
    lecturer_name = ""

    if proposal.student:
        student_name = f"{proposal.student.first_name} {proposal.student.last_name}".strip()

    if proposal.lecturer:
        lecturer_name = f"{proposal.lecturer.first_name} {proposal.lecturer.last_name}".strip()

    calculated_average = get_student_average_grade(db, proposal.student_id)
    stored_average = round(float(proposal.student_average_grade or 0.0), 2)
    displayed_average = calculated_average if calculated_average > 0 else stored_average

    return ThesisProposalResponse(
        id=proposal.id,
        student_id=proposal.student_id,
        student_name=student_name,
        student_email=proposal.student.email if proposal.student else "",
        student_average_grade=displayed_average,
        lecturer_id=proposal.lecturer_id,
        lecturer_name=lecturer_name,
        topic=proposal.topic,
        justification=proposal.justification,
        status=proposal.status.value,
        submitted_at=proposal.submitted_at,
        reviewed_at=proposal.reviewed_at,
    )


def _get_schedule_flags(db: Session) -> dict[str, bool]:
    settings = get_or_create_thesis_settings(db)
    return get_thesis_schedule_flags(settings)


def _to_schedule_response(flags: dict[str, bool], current_user: User, db: Session) -> ThesisScheduleAvailabilityResponse:
    settings = get_or_create_thesis_settings(db)
    is_admin = _is_admin(current_user)
    return ThesisScheduleAvailabilityResponse(
        tab_visible_from=settings.tab_visible_from,
        tab_visible_to=settings.tab_visible_to,
        topic_submission_from=settings.topic_submission_from,
        topic_submission_to=settings.topic_submission_to,
        proposal_selection_from=settings.proposal_selection_from,
        proposal_selection_deadline=settings.proposal_selection_deadline,
        max_approved_proposals=settings.max_approved_proposals,
        can_view_tab=True if is_admin else flags["tab_visible_now"],
        can_submit_topics=True if is_admin else flags["tab_visible_now"] and flags["topic_submission_open"],
        can_select_proposals=True if is_admin else flags["tab_visible_now"] and flags["proposal_selection_open"],
    )


def _ensure_tab_visible(db: Session, current_user: User) -> None:
    if _is_admin(current_user):
        return
    if not _get_schedule_flags(db)["tab_visible_now"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Zakładka prac dyplomowych jest obecnie niedostępna",
        )


def _ensure_submission_open(db: Session, current_user: User) -> None:
    if _is_admin(current_user):
        return
    flags = _get_schedule_flags(db)
    if not flags["tab_visible_now"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Zakładka prac dyplomowych jest obecnie niedostępna",
        )
    if not flags["topic_submission_open"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Termin składania tematów prac dyplomowych jest obecnie zamknięty",
        )


def _ensure_selection_open(db: Session, current_user: User) -> None:
    if _is_admin(current_user):
        return
    flags = _get_schedule_flags(db)
    if not flags["tab_visible_now"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Zakładka prac dyplomowych jest obecnie niedostępna",
        )
    if not flags["proposal_selection_open"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Termin wyboru proponowanych prac dyplomowych już upłynął",
        )


@router.get("/settings", response_model=ThesisScheduleAvailabilityResponse, summary="Pobierz dostępność modułu prac dyplomowych")
def get_schedule_availability(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ThesisScheduleAvailabilityResponse:
    flags = _get_schedule_flags(db)
    return _to_schedule_response(flags, current_user, db)


@router.get("/lecturers", response_model=list[LecturerResponse], summary="List lecturers")
def list_lecturers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(("admin", "student"))),
) -> list[LecturerResponse]:
    _ensure_tab_visible(db, current_user)

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
    current_user: User = Depends(require_role(("admin", "student"))),
) -> ThesisProposalResponse:
    _ensure_submission_open(db, current_user)

    if not _is_admin(current_user):
        own_count = count_own_proposals_for_student(db, current_user.user_id)
        if own_count >= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Możesz złożyć maksymalnie 1 własną propozycję tematu pracy.",
            )

    try:
        proposal = create_thesis_proposal(
            db,
            student_id=current_user.user_id,
            lecturer_id=payload.lecturer_id,
            topic=payload.topic,
            justification=payload.justification,
            student_average_grade=None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return _to_response(proposal, db)


@router.get("/proposals", response_model=list[ThesisProposalResponse], summary="List lecturer thesis proposals")
def list_lecturer_proposals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(("admin", "wykladowca"))),
) -> list[ThesisProposalResponse]:
    _ensure_tab_visible(db, current_user)

    if _is_admin(current_user):
        proposals = get_all_proposals(db)
    else:
        proposals = get_proposals_for_lecturer(db, current_user.user_id)

    responses = [_to_response(proposal, db) for proposal in proposals]
    if not _is_admin(current_user):
        responses.sort(
            key=lambda proposal: (proposal.student_average_grade, proposal.submitted_at),
            reverse=True,
        )
    return responses


@router.get("/my-proposals", response_model=list[ThesisProposalResponse], summary="List student's own thesis proposals")
def list_student_proposals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(("admin", "student"))),
) -> list[ThesisProposalResponse]:
    _ensure_tab_visible(db, current_user)

    proposals = get_proposals_for_student(db, current_user.user_id)
    return [_to_response(proposal, db) for proposal in proposals]


@router.delete(
    "/proposals/{proposal_id}/withdraw",
    status_code=204,
    summary="Student withdraws their own pending proposal",
)
def student_withdraw_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(("admin", "student"))),
) -> None:
    _ensure_tab_visible(db, current_user)

    try:
        result = withdraw_proposal(db, proposal_id, current_user.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")


@router.patch(
    "/proposals/{proposal_id}/status",
    response_model=ThesisProposalResponse,
    summary="Approve or reject thesis proposal",
)
def review_proposal(
    proposal_id: int,
    payload: ThesisProposalStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(("admin", "wykladowca"))),
) -> ThesisProposalResponse:
    _ensure_selection_open(db, current_user)
    settings = get_or_create_thesis_settings(db)

    if _is_admin(current_user):
        proposal = admin_update_proposal_status(
            db,
            proposal_id=proposal_id,
            new_status=ThesisProposalStatus(payload.status.value),
        )
        if proposal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
        return _to_response(proposal, db)

    if payload.status == ThesisProposalStatus.APPROVED:
        approved_count = count_approved_for_lecturer(db, current_user.user_id)
        if approved_count >= settings.max_approved_proposals:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum approved proposals reached ({settings.max_approved_proposals})",
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

    return _to_response(proposal, db)


# ==================== LECTURER TOPICS ====================

def _to_topic_response(topic: LecturerTopic) -> LecturerTopicResponse:
    lecturer_name = ""
    if topic.lecturer:
        lecturer_name = f"{topic.lecturer.first_name} {topic.lecturer.last_name}".strip()
    return LecturerTopicResponse(
        id=topic.id,
        lecturer_id=topic.lecturer_id,
        lecturer_name=lecturer_name,
        topic=topic.topic,
        description=topic.description,
        is_taken=topic.is_taken,
        created_at=topic.created_at,
    )


@router.post(
    "/lecturer-topics",
    response_model=LecturerTopicResponse,
    status_code=201,
    summary="Lecturer proposes a thesis topic",
)
def create_topic(
    payload: LecturerTopicCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("wykladowca")),
) -> LecturerTopicResponse:
    _ensure_selection_open(db, current_user)

    topic = create_lecturer_topic(
        db,
        lecturer_id=current_user.user_id,
        topic=payload.topic,
        description=payload.description,
    )
    db.refresh(topic)
    topic = get_lecturer_topic_by_id(db, topic.id)
    return _to_topic_response(topic)  # type: ignore[arg-type]


@router.get(
    "/lecturer-topics",
    response_model=list[LecturerTopicResponse],
    summary="List lecturer's own proposed topics",
)
def list_own_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("wykladowca")),
) -> list[LecturerTopicResponse]:
    _ensure_tab_visible(db, current_user)

    topics = get_lecturer_topics_by_lecturer(db, current_user.user_id)
    return [_to_topic_response(t) for t in topics]


@router.get(
    "/lecturer-topics/available",
    response_model=list[LecturerTopicResponse],
    summary="List all available lecturer-proposed topics for students",
)
def list_available_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(("admin", "student"))),
) -> list[LecturerTopicResponse]:
    _ensure_tab_visible(db, current_user)

    topics = get_available_lecturer_topics(db)
    return [_to_topic_response(t) for t in topics]


@router.delete(
    "/lecturer-topics/{topic_id}",
    status_code=204,
    summary="Delete lecturer's own proposed topic",
)
def remove_own_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("wykladowca")),
) -> None:
    deleted = delete_lecturer_topic(db, topic_id, current_user.user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nie można usunąć tematu (nie istnieje, nie należy do Ciebie lub został już wybrany).",
        )


@router.post(
    "/lecturer-topics/{topic_id}/select",
    response_model=ThesisProposalResponse,
    status_code=201,
    summary="Student selects a lecturer-proposed topic",
)
def select_lecturer_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(("admin", "student"))),
) -> ThesisProposalResponse:
    _ensure_submission_open(db, current_user)

    if not _is_admin(current_user):
        selected_count = count_selected_topics_for_student(db, current_user.user_id)
        if selected_count >= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Możesz wybrać maksymalnie 1 proponowany temat wykładowcy.",
            )

    topic = get_lecturer_topic_by_id(db, topic_id)
    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temat nie został znaleziony.")
    if topic.is_taken:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ten temat został już wybrany przez innego studenta.")

    proposal = create_thesis_proposal(
        db,
        student_id=current_user.user_id,
        lecturer_id=topic.lecturer_id,
        topic=topic.topic,
        justification=topic.description or "Temat zaproponowany przez promotora.",
        student_average_grade=None,
        lecturer_topic_id=topic.id,
    )
    mark_lecturer_topic_taken(db, topic.id)

    return _to_response(proposal, db)
