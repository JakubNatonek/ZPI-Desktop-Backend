from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.auth.password_utils import hash_password
from app.core.thesis_datetime import normalize_to_utc_minute
from app.cruds.crud_departments_for_user import add_department_to_user
from app.cruds.crud_roles_for_user import add_role_to_user
from app.cruds.crud_user import create_user
from app.models.model_department import Department
from app.models.model_department_for_user import DepartmentsForUser
from app.models.model_role import Role
from app.models.model_role_for_user import RolesForUser
from app.models.model_thesis_proposal import ThesisProposal, ThesisProposalStatus
from app.models.model_user import User


def _ensure_user_with_role(
    db: Session,
    *,
    login: str,
    email: str,
    first_name: str,
    last_name: str,
    role_name: str,
) -> User | None:
    role = db.query(Role).filter(Role.name == role_name).first()
    if role is None:
        return None

    user = db.query(User).filter(User.login == login).first()
    if user is None:
        user = create_user(
            db,
            first_name=first_name,
            last_name=last_name,
            login=login,
            email=email,
            password_hash=hash_password("test123"),
            must_change_password=True,
        )

    role_mapping_exists = (
        db.query(RolesForUser)
        .filter(RolesForUser.user_id == user.user_id, RolesForUser.role_id == role.id)
        .first()
        is not None
    )
    if not role_mapping_exists:
        add_role_to_user(db, user.user_id, role.id)

    first_department = db.query(Department).order_by(Department.id.asc()).first()
    if first_department is not None:
        dept_mapping_exists = (
            db.query(DepartmentsForUser)
            .filter(
                DepartmentsForUser.user_id == user.user_id,
                DepartmentsForUser.department_id == first_department.id,
            )
            .first()
            is not None
        )
        if not dept_mapping_exists:
            add_department_to_user(db, user.user_id, first_department.id)

    return user


def seed_thesis_proposals(db: Session) -> None:
    student = (
        db.query(User)
        .join(RolesForUser, RolesForUser.user_id == User.user_id)
        .join(Role, Role.id == RolesForUser.role_id)
        .filter(Role.name == "student")
        .order_by(User.user_id.asc())
        .first()
    )
    lecturer = (
        db.query(User)
        .join(RolesForUser, RolesForUser.user_id == User.user_id)
        .join(Role, Role.id == RolesForUser.role_id)
        .filter(Role.name == "wykladowca")
        .order_by(User.user_id.asc())
        .first()
    )

    if student is None:
        student = _ensure_user_with_role(
            db,
            login="thesis_student",
            email="thesis_student@example.com",
            first_name="Sample",
            last_name="Student",
            role_name="student",
        )

    if lecturer is None:
        lecturer = _ensure_user_with_role(
            db,
            login="thesis_lecturer",
            email="thesis_lecturer@example.com",
            first_name="Sample",
            last_name="Lecturer",
            role_name="wykladowca",
        )

    if student is None or lecturer is None:
        print("Thesis proposals seed skipped: missing student or lecturer role.")
        return

    now = normalize_to_utc_minute(datetime.now(timezone.utc))
    if now is None:
        return

    sample_rows = [
        {
            "topic": "Analiza wydajnosci systemu rezerwacji sal",
            "justification": "Projekt bada wydajnosc i proponuje optymalizacje procesu rezerwacji.",
            "student_average_grade": 4.3,
            "status": ThesisProposalStatus.PENDING,
            "submitted_at": now - timedelta(days=3),
            "reviewed_at": None,
        },
        {
            "topic": "Integracja harmonogramu zajec z modulem thesis",
            "justification": "Praca opisuje projekt i implementacje integracji danych harmonogramowych.",
            "student_average_grade": 4.7,
            "status": ThesisProposalStatus.APPROVED,
            "submitted_at": now - timedelta(days=10),
            "reviewed_at": now - timedelta(days=1),
        },
    ]

    created = 0
    for row in sample_rows:
        exists = (
            db.query(ThesisProposal)
            .filter(
                ThesisProposal.student_id == student.user_id,
                ThesisProposal.lecturer_id == lecturer.user_id,
                ThesisProposal.topic == row["topic"],
            )
            .first()
        )
        if exists is not None:
            continue

        db.add(
            ThesisProposal(
                student_id=student.user_id,
                lecturer_id=lecturer.user_id,
                student_average_grade=row["student_average_grade"],
                topic=row["topic"],
                justification=row["justification"],
                status=row["status"],
                submitted_at=row["submitted_at"],
                reviewed_at=row["reviewed_at"],
            )
        )
        created += 1

    db.commit()
    print(f"Thesis proposals seeded. Added: {created}")