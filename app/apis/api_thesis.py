from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.models.model_thesis_submission import RequestThesisSubmission
from app.models.model_user import User
from app.schemas.thesis import (
    RequestThesisDefinition,
    RequestThesisField,
    RequestThesisOption,
    RequestThesisSubmissionItem,
    RequestThesisSubmissionsResponse,
    SubmitRequestThesisPayload,
    SubmitRequestThesisResponse,
    UpdateThesisStatusPayload,
)

router = APIRouter(prefix="/request-thesis", tags=["request-thesis"])


def _is_teacher(user: User) -> bool:
    role_name = (user.role.name if user.role else "").strip().lower()
    return role_name in {"wykładowca", "wykladowca", "teacher"} or user.teacher_profile is not None


def _teacher_select_field(db: Session) -> RequestThesisField:
    teachers = db.query(User).all()
    teacher_options = [
        RequestThesisOption(
            label=f"{teacher.first_name} {teacher.last_name}",
            value=str(teacher.user_id),
        )
        for teacher in teachers
        if _is_teacher(teacher)
    ]

    return RequestThesisField(
        key="teacherUserId",
        label="Adresat (wykładowca)",
        type="select",
        required=True,
        placeholder="Wybierz wykładowcę",
        options=teacher_options,
    )


def _document_types(db: Session) -> List[RequestThesisDefinition]:
    teacher_field = _teacher_select_field(db)
    return [
        RequestThesisDefinition(
            id=1,
            name="Podanie o warunkowy wpis",
            description="Wniosek o warunkowe zaliczenie semestru.",
            templateFileName="podanie-warunkowy-wpis.pdf",
            fields=[
                RequestThesisField(key="studentIndex", label="Numer albumu", type="text", required=True, placeholder="Np. 123456"),
                RequestThesisField(
                    key="semester",
                    label="Semestr",
                    type="select",
                    required=True,
                    options=[
                        RequestThesisOption(label="1", value="1"),
                        RequestThesisOption(label="2", value="2"),
                        RequestThesisOption(label="3", value="3"),
                        RequestThesisOption(label="4", value="4"),
                        RequestThesisOption(label="5", value="5"),
                        RequestThesisOption(label="6", value="6"),
                        RequestThesisOption(label="7", value="7"),
                    ],
                ),
                RequestThesisField(key="reason", label="Uzasadnienie", type="textarea", required=True, placeholder="Opisz przyczynę złożenia podania."),
                teacher_field,
            ],
        ),
        RequestThesisDefinition(
            id=2,
            name="Wniosek o indywidualną organizację studiów",
            description="Formularz do złożenia prośby o IOS.",
            templateFileName="wniosek-ios.pdf",
            fields=[
                RequestThesisField(key="studentIndex", label="Numer albumu", type="text", required=True, placeholder="Np. 123456"),
                RequestThesisField(key="contactEmail", label="Email kontaktowy", type="email", required=True, placeholder="student@uczelnia.pl"),
                RequestThesisField(key="requestedFromDate", label="Data od", type="date", required=True),
                RequestThesisField(key="reason", label="Powód", type="textarea", required=True, placeholder="Opisz powód prośby o IOS."),
                teacher_field,
            ],
        ),
        RequestThesisDefinition(
            id=3,
            name="Wniosek o duplikat legitymacji",
            description="Wniosek o wydanie nowej legitymacji studenckiej.",
            templateFileName="wniosek-duplikat-legitymacji.pdf",
            fields=[
                RequestThesisField(key="studentIndex", label="Numer albumu", type="text", required=True),
                RequestThesisField(key="lostDate", label="Data utraty dokumentu", type="date", required=True),
                RequestThesisField(
                    key="issueDescription",
                    label="Opis sytuacji",
                    type="textarea",
                    required=True,
                    placeholder="Krótki opis utraty/zniszczenia legitymacji.",
                ),
                teacher_field,
            ],
        ),
    ]


@router.get(
    "/types",
    response_model=List[RequestThesisDefinition],
    summary="Pobierz listę typów dokumentów",
)
def get_document_types(db: Session = Depends(get_db)) -> List[RequestThesisDefinition]:
    return _document_types(db)


@router.get(
    "/types/{document_type_id}/template",
    summary="Pobierz wzór dokumentu",
)
def get_document_template(document_type_id: int, db: Session = Depends(get_db)) -> Response:
    document = next((doc for doc in _document_types(db) if doc.id == document_type_id), None)
    if document is None:
        raise HTTPException(status_code=404, detail="Document type not found")

    content = (
        f"Wzór dokumentu: {document.name}\n"
        f"Opis: {document.description}\n"
        "\n"
        "Wersja produkcyjna powinna zwracać PDF lub DOCX.\n"
    ).encode("utf-8")

    headers = {
        "Content-Disposition": f"attachment; filename={document.templateFileName}",
    }
    return Response(content=content, media_type="text/plain; charset=utf-8", headers=headers)


@router.post(
    "/submissions",
    response_model=SubmitRequestThesisResponse,
    summary="Wyślij dokument",
)
def submit_document(
    payload: SubmitRequestThesisPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmitRequestThesisResponse:
    document = next((doc for doc in _document_types(db) if doc.id == payload.documentTypeId), None)
    if document is None:
        raise HTTPException(status_code=404, detail="Document type not found")

    teacher_user_id = payload.teacherUserId
    if teacher_user_id is None:
        raw_value = payload.values.get("teacherUserId")
        if isinstance(raw_value, (int, float)):
            teacher_user_id = int(raw_value)
        elif isinstance(raw_value, str) and raw_value.isdigit():
            teacher_user_id = int(raw_value)

    if teacher_user_id is None:
        raise HTTPException(status_code=400, detail="teacherUserId is required")

    teacher = db.query(User).filter(User.user_id == teacher_user_id).first()
    if teacher is None or not _is_teacher(teacher):
        raise HTTPException(status_code=400, detail="Invalid teacherUserId")

    submission = RequestThesisSubmission(
        document_type_id=document.id,
        document_type_name=document.name,
        values=payload.values,
        is_approved=False,
        student_user_id=current_user.user_id,
        teacher_user_id=teacher_user_id,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    return SubmitRequestThesisResponse(id=submission.id, status="SENT")


@router.get(
    "/submissions",
    response_model=RequestThesisSubmissionsResponse,
    summary="Pobierz dokumenty użytkownika",
)
def list_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RequestThesisSubmissionsResponse:
    if _is_teacher(current_user):
        items = (
            db.query(RequestThesisSubmission)
            .filter(RequestThesisSubmission.teacher_user_id == current_user.user_id)
            .order_by(RequestThesisSubmission.submitted_at.desc())
            .all()
        )
        viewer_role = "teacher"
    else:
        items = (
            db.query(RequestThesisSubmission)
            .filter(RequestThesisSubmission.student_user_id == current_user.user_id)
            .order_by(RequestThesisSubmission.submitted_at.desc())
            .all()
        )
        viewer_role = "student"

    response_items = [
        RequestThesisSubmissionItem(
            id=item.id,
            documentTypeId=item.document_type_id,
            documentName=item.document_type_name,
            submittedAt=item.submitted_at,
            isApproved=item.is_approved,
            values=item.values or {},
            studentUserId=item.student_user_id,
            teacherUserId=item.teacher_user_id,
        )
        for item in items
    ]

    return RequestThesisSubmissionsResponse(viewerRole=viewer_role, items=response_items)


@router.patch(
    "/submissions/{submission_id}/status",
    response_model=RequestThesisSubmissionItem,
    summary="Ustaw status dokumentu",
)
def update_submission_status(
    submission_id: int,
    payload: UpdateThesisStatusPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RequestThesisSubmissionItem:
    if not _is_teacher(current_user):
        raise HTTPException(status_code=403, detail="Only teachers can update status")

    submission = db.query(RequestThesisSubmission).filter(RequestThesisSubmission.id == submission_id).first()
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.teacher_user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Submission is not assigned to current teacher")

    submission.is_approved = payload.isApproved
    db.add(submission)
    db.commit()
    db.refresh(submission)

    return RequestThesisSubmissionItem(
        id=submission.id,
        documentTypeId=submission.document_type_id,
        documentName=submission.document_type_name,
        submittedAt=submission.submitted_at,
        isApproved=submission.is_approved,
        values=submission.values or {},
        studentUserId=submission.student_user_id,
        teacherUserId=submission.teacher_user_id,
    )
