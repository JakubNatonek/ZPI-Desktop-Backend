from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.model_group import Group
from app.models.model_grade import GradeRecord
from app.models.model_student import Student
from app.models.model_teacher import Teacher
from app.models.model_user import Department, Role, User


DEFAULT_PASSWORD_HASH = "$2b$12$WBVbY5qn9EMmPJHCzTY1JenHu7vFrRC/NQn.8XSy8k2OEtPRvS8lO"


def _seed_departments_and_roles(db: Session) -> None:
    departments = [
        {"id": 1, "name": "admin"},
        {"id": 2, "name": "Informatyka"},
        {"id": 3, "name": "Fizyka"},
    ]
    for dep in departments:
        if not db.query(Department).filter_by(id=dep["id"]).first():
            db.add(Department(**dep))

    roles = [
        {"id": 1, "name": "admin"},
        {"id": 2, "name": "wykladowca"},
        {"id": 3, "name": "student"},
    ]
    for role in roles:
        if not db.query(Role).filter_by(id=role["id"]).first():
            db.add(Role(**role))


def _seed_groups(db: Session) -> Group:
    group = db.query(Group).filter(Group.code == "P1").first()
    if group:
        return group

    group = Group(
        specialization="Informatyka",
        code="P1",
        year=3,
        studies_type="Stacjonarne",
    )
    db.add(group)
    db.flush()
    return group


def _seed_user(db: Session, payload: dict[str, object]) -> User:
    existing = db.query(User).filter(User.login == payload["login"]).first()
    if existing:
        return existing

    user = User(**payload)
    db.add(user)
    db.flush()
    return user


def _seed_student_profile(db: Session, user_id: int, group_id: int) -> None:
    existing = db.query(Student).filter(Student.user_id == user_id).first()
    if existing:
        return

    db.add(
        Student(
            user_id=user_id,
            index_number="s42000",
            group_id=group_id,
            semester=6,
        )
    )


def _seed_teacher_profile(db: Session, user_id: int) -> None:
    existing = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if existing:
        return

    db.add(
        Teacher(
            user_id=user_id,
            title="dr inz.",
            prop=None,
        )
    )


def _seed_grade_records(db: Session, student_id: int, lecturer_id: int) -> None:
    existing = (
        db.query(GradeRecord)
        .filter(
            GradeRecord.student_id == student_id,
            GradeRecord.lecturer_id == lecturer_id,
        )
        .first()
    )
    if existing:
        return

    records = [
        {
            "semester": 6,
            "subject_name": "Programowanie Mobilne",
            "component_label": "Ocena koncowa",
            "component_info": "",
            "grade_value": 4.5,
            "is_final": True,
            "sort_order": 0,
        },
        {
            "semester": 6,
            "subject_name": "Programowanie Mobilne",
            "component_label": "Kolokwium 1",
            "component_info": "2026-03-08",
            "grade_value": 4.0,
            "is_final": False,
            "sort_order": 1,
        },
        {
            "semester": 6,
            "subject_name": "Programowanie Mobilne",
            "component_label": "Projekt",
            "component_info": "Aplikacja Ionic",
            "grade_value": 5.0,
            "is_final": False,
            "sort_order": 2,
        },
        {
            "semester": 5,
            "subject_name": "Bazy Danych",
            "component_label": "Ocena koncowa",
            "component_info": "",
            "grade_value": 4.0,
            "is_final": True,
            "sort_order": 0,
        },
        {
            "semester": 5,
            "subject_name": "Bazy Danych",
            "component_label": "Laboratorium",
            "component_info": "Projekt ERD",
            "grade_value": 4.0,
            "is_final": False,
            "sort_order": 1,
        },
    ]

    for record in records:
        db.add(
            GradeRecord(
                student_id=student_id,
                lecturer_id=lecturer_id,
                semester=record["semester"],
                subject_name=record["subject_name"],
                component_label=record["component_label"],
                component_info=record["component_info"],
                grade_value=record["grade_value"],
                is_final=record["is_final"],
                sort_order=record["sort_order"],
            )
        )


def seed_initial_data() -> None:
    db: Session = SessionLocal()
    try:
        _seed_departments_and_roles(db)
        db.flush()

        default_group = _seed_groups(db)

        admin = _seed_user(
            db,
            {
                "first_name": "admin",
                "last_name": "admin",
                "login": "admin",
                "email": "admin@admin.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "plain_password": None,
                "must_change_password": False,
                "role_id": 1,
                "department_id": 1,
            },
        )

        student = _seed_user(
            db,
            {
                "first_name": "student",
                "last_name": "student",
                "login": "stu",
                "email": "student@student.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "plain_password": None,
                "must_change_password": False,
                "role_id": 3,
                "department_id": 2,
            },
        )

        lecturer = _seed_user(
            db,
            {
                "first_name": "wykladowca",
                "last_name": "wykladowca",
                "login": "wyk",
                "email": "wykladowca@wykladowca.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "plain_password": None,
                "must_change_password": False,
                "role_id": 2,
                "department_id": 2,
            },
        )

        _ = admin
        _seed_student_profile(db, student.user_id, default_group.id)
        _seed_teacher_profile(db, lecturer.user_id)
        _seed_grade_records(db, student.user_id, lecturer.user_id)

        db.commit()
        print("Initial data seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_initial_data()
