from collections import defaultdict

from sqlalchemy.orm import Session, joinedload

from app.models.model_grade import GradeRecord
from app.models.model_user import User
from app.schemas.grade import (
    LecturerSemesterGradesResponse,
    PartialGradeResponse,
    SemesterGradesResponse,
    StudentGradesResponse,
    SubjectGradeResponse,
)


LECTURER_ROLE_NAMES = {"lecturer", "wykladowca", "cwiczenia", "laboratorium", "seminarium"}
STUDENT_ROLE_NAMES = {"student"}


def _to_grade_string(value: float) -> str:
    as_text = f"{value:.1f}".rstrip("0").rstrip(".")
    return as_text if as_text else "0"


def _is_lecturer_user(user: User) -> bool:
    role_name = (user.role.name if user.role else "").strip().lower()
    return role_name in LECTURER_ROLE_NAMES


def _is_student_user(user: User) -> bool:
    role_name = (user.role.name if user.role else "").strip().lower()
    return role_name in STUDENT_ROLE_NAMES


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

    response: list[SemesterGradesResponse] = []
    for semester in sorted(semester_subject_map.keys(), reverse=True):
        subjects: list[SubjectGradeResponse] = []
        for subject_name in sorted(semester_subject_map[semester].keys()):
            subject_records = semester_subject_map[semester][subject_name]
            final_record = next((record for record in subject_records if record.is_final), None)
            partial_records = [record for record in subject_records if not record.is_final]
            teacher = ""
            if final_record and final_record.lecturer:
                teacher = f"{final_record.lecturer.first_name} {final_record.lecturer.last_name}".strip()
            elif partial_records and partial_records[0].lecturer:
                teacher = f"{partial_records[0].lecturer.first_name} {partial_records[0].lecturer.last_name}".strip()

            subjects.append(
                SubjectGradeResponse(
                    subject=subject_name,
                    teacher=teacher,
                    final_grade=_to_grade_string(final_record.grade_value) if final_record else "Brak",
                    partial_grades=[
                        PartialGradeResponse(
                            id=record.id,
                            label=record.component_label or "Ocena czastkowa",
                            grade=_to_grade_string(record.grade_value),
                            info=record.component_info or "",
                        )
                        for record in partial_records
                    ],
                )
            )

        response.append(
            SemesterGradesResponse(
                semester=semester,
                semester_label=f"Semestr {semester}",
                subjects=subjects,
            )
        )

    return response


def get_lecturer_semester_grades(db: Session, lecturer_id: int) -> list[LecturerSemesterGradesResponse]:
    records = (
        db.query(GradeRecord)
        .options(joinedload(GradeRecord.student), joinedload(GradeRecord.lecturer))
        .filter(GradeRecord.lecturer_id == lecturer_id)
        .order_by(
            GradeRecord.semester.desc(),
            GradeRecord.student_id.asc(),
            GradeRecord.subject_name.asc(),
            GradeRecord.sort_order.asc(),
            GradeRecord.id.asc(),
        )
        .all()
    )

    semester_student_subject_map: dict[int, dict[int, dict[str, list[GradeRecord]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for record in records:
        semester_student_subject_map[record.semester][record.student_id][record.subject_name].append(record)

    response: list[LecturerSemesterGradesResponse] = []
    for semester in sorted(semester_student_subject_map.keys(), reverse=True):
        students_payload: list[StudentGradesResponse] = []
        for student_id in sorted(semester_student_subject_map[semester].keys()):
            subject_map = semester_student_subject_map[semester][student_id]
            first_subject_records = next(iter(subject_map.values()))
            any_record = first_subject_records[0] if first_subject_records else None
            student_name = ""
            if any_record and any_record.student:
                student_name = f"{any_record.student.first_name} {any_record.student.last_name}".strip()

            subjects_payload: list[SubjectGradeResponse] = []
            for subject_name in sorted(subject_map.keys()):
                subject_records = subject_map[subject_name]
                final_record = next((record for record in subject_records if record.is_final), None)
                partial_records = [record for record in subject_records if not record.is_final]
                teacher = ""
                if final_record and final_record.lecturer:
                    teacher = f"{final_record.lecturer.first_name} {final_record.lecturer.last_name}".strip()

                subjects_payload.append(
                    SubjectGradeResponse(
                        subject=subject_name,
                        teacher=teacher,
                        final_grade=_to_grade_string(final_record.grade_value) if final_record else "Brak",
                        partial_grades=[
                            PartialGradeResponse(
                                id=record.id,
                                label=record.component_label or "Ocena czastkowa",
                                grade=_to_grade_string(record.grade_value),
                                info=record.component_info or "",
                            )
                            for record in partial_records
                        ],
                    )
                )

            students_payload.append(
                StudentGradesResponse(
                    student_id=student_id,
                    student_name=student_name,
                    subjects=subjects_payload,
                )
            )

        response.append(
            LecturerSemesterGradesResponse(
                semester=semester,
                semester_label=f"Semestr {semester}",
                students=students_payload,
            )
        )

    return response


def replace_subject_grades(
    db: Session,
    lecturer_id: int,
    student_id: int,
    semester: int,
    subject_name: str,
    final_grade: float,
    partial_grades: list[dict[str, object]],
) -> None:
    student = db.query(User).filter(User.user_id == student_id).first()
    if student is None:
        raise ValueError("Student does not exist")
    if not _is_student_user(student):
        raise ValueError("Selected user is not a student")

    lecturer = db.query(User).filter(User.user_id == lecturer_id).first()
    if lecturer is None:
        raise ValueError("Lecturer does not exist")
    if not _is_lecturer_user(lecturer):
        raise ValueError("Current user is not a lecturer")

    (
        db.query(GradeRecord)
        .filter(
            GradeRecord.lecturer_id == lecturer_id,
            GradeRecord.student_id == student_id,
            GradeRecord.semester == semester,
            GradeRecord.subject_name == subject_name,
        )
        .delete()
    )

    db.add(
        GradeRecord(
            lecturer_id=lecturer_id,
            student_id=student_id,
            semester=semester,
            subject_name=subject_name,
            component_label="Ocena koncowa",
            component_info="",
            grade_value=final_grade,
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
                subject_name=subject_name,
                component_label=str(partial_grade.get("label") or "Ocena czastkowa"),
                component_info=str(partial_grade.get("info") or ""),
                grade_value=float(partial_grade.get("grade") or 0),
                is_final=False,
                sort_order=index,
            )
        )

    db.commit()
