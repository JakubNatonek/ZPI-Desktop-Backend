from collections import defaultdict
from datetime import date
import re

from sqlalchemy.orm import Session, joinedload

from app.cruds.crud_roles_for_user import get_roles_for_user
from app.models.model_grade import GradeRecord
from app.models.model_semestr import Semestr
from app.models.model_student import Student
from app.models.model_subject import Subject
from app.models.model_user import User
from app.schemas.grade import (
    LecturerSemesterGradesResponse,
    PartialGradeResponse,
    SemesterOptionResponse,
    SemesterGradesResponse,
    StudentGradesResponse,
    SubjectGradeResponse,
)


LECTURER_ROLE_NAMES = {"lecturer", "wykladowca", "wykładowca", "cwiczenia", "ćwiczenia", "laboratorium", "seminarium"}
STUDENT_ROLE_NAMES = {"student"}
ADMIN_ROLE_NAMES = {"admin"}
ROLE_NAME_TO_SUBJECT_TYPES = {
    "lecturer": {"wyklad"},
    "wykladowca": {"wyklad"},
    "wykładowca": {"wyklad"},
    "cwiczenia": {"cwiczenia"},
    "ćwiczenia": {"cwiczenia"},
    "laboratorium": {"laboratorium"},
    "seminarium": {"seminarium"},
}


def _user_role_names(db: Session, user_id: int) -> set[str]:
    return {
        role.name.strip().lower()
        for role in get_roles_for_user(db, user_id)
        if role.name and role.name.strip()
    }


def _subject_types_for_lecturer_roles(role_names: set[str]) -> set[str]:
    allowed_types: set[str] = set()
    for role_name in role_names:
        allowed_types.update(ROLE_NAME_TO_SUBJECT_TYPES.get(role_name, set()))
    return allowed_types


def _lecturer_allowed_subject_names(db: Session, lecturer_id: int) -> list[str]:
    role_names = _user_role_names(db, lecturer_id)
    allowed_subject_types = _subject_types_for_lecturer_roles(role_names)
    subject_names: set[str] = set()

    if allowed_subject_types:
        for (subject_name,) in (
            db.query(Subject.name)
            .filter(Subject.type.in_(allowed_subject_types))
            .distinct()
            .all()
        ):
            if subject_name and subject_name.strip():
                subject_names.add(subject_name.strip())

    # Keep already assigned subjects available even if role mapping changes over time.
    for (subject_name,) in (
        db.query(GradeRecord.subject_name)
        .filter(GradeRecord.lecturer_id == lecturer_id)
        .distinct()
        .all()
    ):
        if subject_name and subject_name.strip():
            subject_names.add(subject_name.strip())

    return sorted(subject_names)


def get_current_semester(db: Session) -> Semestr | None:
    return (
        db.query(Semestr)
        .order_by(
            Semestr.data_zakonczenia.desc(),
            Semestr.data_rozpoczecia.desc(),
            Semestr.id.desc(),
        )
        .first()
    )


def _to_grade_string(value: float) -> str:
    as_text = f"{value:.1f}".rstrip("0").rstrip(".")
    return as_text if as_text else "0"


def _semester_type_from_name(name: str | None) -> str | None:
    if not name:
        return None

    normalized_name = name.lower()
    if "zim" in normalized_name:
        return "zimowy"
    if "let" in normalized_name:
        return "letni"
    return None


def _semester_type(semester_row: Semestr | None, semester_id: int) -> str:
    if semester_row is not None:
        type_from_name = _semester_type_from_name(semester_row.nazwa)
        if type_from_name is not None:
            return type_from_name

        return "zimowy" if semester_row.data_rozpoczecia.month >= 7 else "letni"

    return "zimowy" if semester_id % 2 == 1 else "letni"


def _semester_year(semester_row: Semestr | None) -> int | None:
    if semester_row is None:
        return None

    year_matches = re.findall(r"\b(19\d{2}|20\d{2})\b", semester_row.nazwa or "")
    if year_matches:
        return max(int(year_text) for year_text in year_matches)

    return semester_row.data_rozpoczecia.year


def _semester_label(semester_row: Semestr | None, semester_id: int) -> str:
    semester_type = _semester_type(semester_row, semester_id)
    semester_year = _semester_year(semester_row)
    if semester_year is not None:
        return f"Semestr {semester_type} {semester_year}"

    return f"Semestr {semester_id} ({semester_type})"


def _semester_sort_key(semester_id: int, semester_lookup: dict[int, Semestr]) -> tuple[date, date, int]:
    semester_row = semester_lookup.get(semester_id)
    if semester_row is None:
        return (date.min, date.min, semester_id)

    return (semester_row.data_zakonczenia, semester_row.data_rozpoczecia, semester_row.id)


def _semester_lookup(db: Session, semester_ids: set[int]) -> dict[int, Semestr]:
    if not semester_ids:
        return {}

    semesters = db.query(Semestr).filter(Semestr.id.in_(semester_ids)).all()
    return {semester.id: semester for semester in semesters}


def _weighted_average(grades: list[tuple[float, float]]) -> str:
    total_weight = sum(w for _, w in grades)
    if total_weight == 0:
        return "—"
    avg = sum(g * w for g, w in grades) / total_weight
    return f"{avg:.2f}"


def _is_lecturer_user(db: Session, user: User) -> bool:
    return bool(_user_role_names(db, user.user_id).intersection(LECTURER_ROLE_NAMES))


def _is_student_user(db: Session, user: User) -> bool:
    return bool(_user_role_names(db, user.user_id).intersection(STUDENT_ROLE_NAMES))


def _build_subject_response(
    subject_name: str,
    subject_records: list[GradeRecord],
    fallback_teacher: str = "",
) -> SubjectGradeResponse:
    final_record = next((r for r in subject_records if r.is_final), None)
    partial_records = sorted(
        (r for r in subject_records if not r.is_final),
        key=lambda record: (record.sort_order, record.id),
    )

    teacher = fallback_teacher
    if final_record and final_record.lecturer:
        teacher = f"{final_record.lecturer.first_name} {final_record.lecturer.last_name}".strip()
    elif partial_records and partial_records[0].lecturer:
        teacher = f"{partial_records[0].lecturer.first_name} {partial_records[0].lecturer.last_name}".strip()

    subject_weight = final_record.weight if final_record else 1.0

    partial_grade_values = [(r.grade_value, r.weight) for r in partial_records]
    avg = _weighted_average(partial_grade_values) if partial_grade_values else "—"

    return SubjectGradeResponse(
        subject=subject_name,
        teacher=teacher,
        final_grade=_to_grade_string(final_record.grade_value) if final_record else "Brak",
        subject_weight=subject_weight,
        weighted_average=avg,
        partial_grades=[
            PartialGradeResponse(
                id=r.id,
                label=r.component_label or "Ocena czastkowa",
                grade=_to_grade_string(r.grade_value),
                weight=r.weight,
                info=r.component_info or "",
            )
            for r in partial_records
        ],
    )


def _build_semester_average(subjects: list[SubjectGradeResponse]) -> str:
    grades_weights = []
    for s in subjects:
        if s.final_grade != "Brak":
            try:
                grades_weights.append((float(s.final_grade.replace(",", ".")), s.subject_weight))
            except ValueError:
                pass
    return _weighted_average(grades_weights) if grades_weights else "—"


def get_student_semester_grades(db: Session, student_id: int) -> list[SemesterGradesResponse]:
    records = (
        db.query(GradeRecord)
        .options(joinedload(GradeRecord.lecturer))
        .filter(GradeRecord.student_id == student_id)
        .order_by(GradeRecord.semester.desc(), GradeRecord.subject_name.asc(), GradeRecord.sort_order.asc(), GradeRecord.id.asc())
        .all()
    )

    semester_subject_map: dict[int, dict[str, list[GradeRecord]]] = defaultdict(lambda: defaultdict(list))
    for record in records:
        semester_subject_map[record.semester][record.subject_name].append(record)

    semester_lookup = _semester_lookup(db, set(semester_subject_map.keys()))

    response: list[SemesterGradesResponse] = []
    for semester in sorted(
        semester_subject_map.keys(),
        key=lambda semester_id: _semester_sort_key(semester_id, semester_lookup),
        reverse=True,
    ):
        semester_row = semester_lookup.get(semester)
        subjects: list[SubjectGradeResponse] = []
        for subject_name in sorted(semester_subject_map[semester].keys()):
            subjects.append(_build_subject_response(subject_name, semester_subject_map[semester][subject_name]))

        response.append(
            SemesterGradesResponse(
                semester=semester,
                semester_label=_semester_label(semester_row, semester),
                semester_type=_semester_type(semester_row, semester),
                semester_average=_build_semester_average(subjects),
                subjects=subjects,
            )
        )

    return response


def get_lecturer_semester_grades(
    db: Session,
    lecturer_id: int,
    current_only: bool = True,
) -> list[LecturerSemesterGradesResponse]:
    lecturer = db.query(User).filter(User.user_id == lecturer_id).first()
    if lecturer is None:
        return []

    lecturer_display_name = f"{lecturer.first_name} {lecturer.last_name}".strip()
    lecturer_subject_names = _lecturer_allowed_subject_names(db, lecturer_id)
    current_semester = get_current_semester(db)
    current_semester_id = current_semester.id if current_semester is not None else None

    if current_only:
        if current_semester is None:
            return []
        semesters = [current_semester]
    else:
        semesters = (
            db.query(Semestr)
            .order_by(
                Semestr.data_zakonczenia.desc(),
                Semestr.data_rozpoczecia.desc(),
                Semestr.id.desc(),
            )
            .all()
        )

    response: list[LecturerSemesterGradesResponse] = []
    for semester in semesters:
        students = (
            db.query(Student)
            .options(joinedload(Student.user))
            .order_by(Student.id.asc())
            .all()
        )

        students_payload: list[StudentGradesResponse] = []
        for student in students:
            records = (
                db.query(GradeRecord)
                .options(joinedload(GradeRecord.lecturer))
                .filter(
                    GradeRecord.lecturer_id == lecturer_id,
                    GradeRecord.student_id == student.user_id,
                    GradeRecord.semester == semester.id,
                )
                .order_by(GradeRecord.subject_name.asc(), GradeRecord.sort_order.asc(), GradeRecord.id.asc())
                .all()
            )

            subject_map = defaultdict(list)
            for record in records:
                subject_map[record.subject_name].append(record)

            for subject_name in lecturer_subject_names:
                subject_map.setdefault(subject_name, [])

            subjects_payload = [
                _build_subject_response(
                    subject_name,
                    subject_map[subject_name],
                    fallback_teacher=lecturer_display_name,
                )
                for subject_name in sorted(subject_map.keys())
            ]

            students_payload.append(
                StudentGradesResponse(
                    student_id=student.user_id,
                    student_name=(
                        f"{student.user.first_name} {student.user.last_name}".strip()
                        if student.user
                        else ""
                    ),
                    album_number=student.user.album_number if student.user else "",
                    subjects=subjects_payload,
                )
            )

        response.append(
            LecturerSemesterGradesResponse(
                semester=semester.id,
                semester_label=_semester_label(semester, semester.id),
                semester_type=_semester_type(semester, semester.id),
                is_current=(current_semester_id is not None and semester.id == current_semester_id),
                students=students_payload,
            )
        )
    return response


def list_semester_options(db: Session) -> list[SemesterOptionResponse]:
    current_semester = get_current_semester(db)
    current_semester_id = current_semester.id if current_semester is not None else None
    semesters = (
        db.query(Semestr)
        .order_by(
            Semestr.data_zakonczenia.desc(),
            Semestr.data_rozpoczecia.desc(),
            Semestr.id.desc(),
        )
        .all()
    )

    return [
        SemesterOptionResponse(
            semester=semester.id,
            semester_label=_semester_label(semester, semester.id),
            semester_type=_semester_type(semester, semester.id),
            is_current=(current_semester_id is not None and semester.id == current_semester_id),
        )
        for semester in semesters
    ]


def get_student_grades_by_album(db: Session, album_number: str) -> tuple[list[SemesterGradesResponse], dict]:
    student = db.query(User).filter(User.album_number == album_number).first()
    if student is None:
        raise ValueError("Student o podanym numerze albumu nie istnieje")

    semesters = get_student_semester_grades(db, student.user_id)
    student_info = {
        "student_id": student.user_id,
        "student_name": f"{student.first_name} {student.last_name}".strip(),
        "album_number": student.album_number,
    }
    return semesters, student_info


def replace_subject_grades(
    db: Session,
    lecturer_id: int,
    student_id: int,
    semester: int,
    subject_name: str,
    final_grade: float,
    subject_weight: float,
    partial_grades: list[dict[str, object]],
    allow_subject_weight_edit: bool = True,
) -> None:
    student = db.query(User).filter(User.user_id == student_id).first()
    if student is None:
        raise ValueError("Student does not exist")
    if not _is_student_user(db, student):
        raise ValueError("Selected user is not a student")

    lecturer = db.query(User).filter(User.user_id == lecturer_id).first()
    if lecturer is None:
        raise ValueError("Lecturer does not exist")
    if not _is_lecturer_user(db, lecturer):
        raise ValueError("Current user is not a lecturer")

    normalized_subject_name = subject_name.strip()
    if not normalized_subject_name:
        raise ValueError("Subject name cannot be empty")

    subject_exists = db.query(Subject.id).filter(Subject.name == normalized_subject_name).first()
    if subject_exists is None:
        raise ValueError("Selected subject does not exist")

    allowed_subject_names = set(_lecturer_allowed_subject_names(db, lecturer_id))
    if allowed_subject_names and normalized_subject_name not in allowed_subject_names:
        raise ValueError("Lecturer is not allowed to grade this subject")

    existing_final_record = (
        db.query(GradeRecord)
        .filter(
            GradeRecord.lecturer_id == lecturer_id,
            GradeRecord.student_id == student_id,
            GradeRecord.semester == semester,
            GradeRecord.subject_name == normalized_subject_name,
            GradeRecord.is_final == True,  # noqa: E712
        )
        .first()
    )

    resolved_subject_weight = subject_weight
    if not allow_subject_weight_edit:
        resolved_subject_weight = existing_final_record.weight if existing_final_record else 1.0

    (
        db.query(GradeRecord)
        .filter(
            GradeRecord.lecturer_id == lecturer_id,
            GradeRecord.student_id == student_id,
            GradeRecord.semester == semester,
            GradeRecord.subject_name == normalized_subject_name,
        )
        .delete()
    )

    db.add(
        GradeRecord(
            lecturer_id=lecturer_id,
            student_id=student_id,
            semester=semester,
            subject_name=normalized_subject_name,
            component_label="Ocena koncowa",
            component_info="",
            grade_value=final_grade,
            weight=resolved_subject_weight,
            is_final=True,
            sort_order=0,
        )
    )

    for index, partial_grade in enumerate(partial_grades, start=1):
        db.add(
            GradeRecord(
                lecturer_id=lecturer_id,
                student_id=student_id,
                semester=semester,
                subject_name=normalized_subject_name,
                component_label=str(partial_grade.get("label") or "Ocena czastkowa"),
                component_info=str(partial_grade.get("info") or ""),
                grade_value=float(partial_grade.get("grade") or 0),
                weight=float(partial_grade.get("weight") or 1.0),
                is_final=False,
                sort_order=index,
            )
        )

    db.commit()


def admin_replace_subject_grades(
    db: Session,
    lecturer_id: int | None,
    student_id: int,
    semester: int,
    subject_name: str,
    final_grade: float,
    subject_weight: float,
    partial_grades: list[dict[str, object]],
    fallback_lecturer_id: int | None = None,
) -> None:
    student = db.query(User).filter(User.user_id == student_id).first()
    if student is None:
        raise ValueError("Student does not exist")

    normalized_subject_name = subject_name.strip()
    if not normalized_subject_name:
        raise ValueError("Subject name cannot be empty")

    subject_exists = db.query(Subject.id).filter(Subject.name == normalized_subject_name).first()
    if subject_exists is None:
        raise ValueError("Selected subject does not exist")

    existing_record = (
        db.query(GradeRecord)
        .filter(
            GradeRecord.student_id == student_id,
            GradeRecord.semester == semester,
            GradeRecord.subject_name == normalized_subject_name,
        )
        .order_by(GradeRecord.is_final.desc(), GradeRecord.id.asc())
        .first()
    )

    resolved_lecturer_id = lecturer_id
    if resolved_lecturer_id is None and existing_record is not None:
        resolved_lecturer_id = existing_record.lecturer_id
    if resolved_lecturer_id is None:
        resolved_lecturer_id = fallback_lecturer_id
    if resolved_lecturer_id is None:
        raise ValueError("Cannot resolve lecturer for grade update")

    lecturer_user = db.query(User).filter(User.user_id == resolved_lecturer_id).first()
    if lecturer_user is None:
        raise ValueError("Provided lecturer does not exist")

    (
        db.query(GradeRecord)
        .filter(
            GradeRecord.student_id == student_id,
            GradeRecord.semester == semester,
            GradeRecord.subject_name == normalized_subject_name,
        )
        .delete()
    )

    db.add(
        GradeRecord(
            lecturer_id=resolved_lecturer_id,
            student_id=student_id,
            semester=semester,
            subject_name=normalized_subject_name,
            component_label="Ocena koncowa",
            component_info="",
            grade_value=final_grade,
            weight=subject_weight,
            is_final=True,
            sort_order=0,
        )
    )

    for index, partial_grade in enumerate(partial_grades, start=1):
        db.add(
            GradeRecord(
                lecturer_id=resolved_lecturer_id,
                student_id=student_id,
                semester=semester,
                subject_name=normalized_subject_name,
                component_label=str(partial_grade.get("label") or "Ocena czastkowa"),
                component_info=str(partial_grade.get("info") or ""),
                grade_value=float(partial_grade.get("grade") or 0),
                weight=float(partial_grade.get("weight") or 1.0),
                is_final=False,
                sort_order=index,
            )
        )

    db.commit()
