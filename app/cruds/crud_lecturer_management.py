from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.model_department import Department
from app.models.model_department_for_user import DepartmentsForUser
from app.models.model_role import Role
from app.models.model_role_for_user import RolesForUser
from app.models.model_teacher import Teacher
from app.models.model_user import User


def get_lecturers(
    db: Session,
    department_id: int | None = None,
) -> list[dict]:
    """Return lecturer records with user, teacher profile, and department info."""
    query = (
        db.query(User)
        .join(RolesForUser, RolesForUser.user_id == User.user_id)
        .join(Role, RolesForUser.role_id == Role.id)
        .filter(func.lower(Role.name).in_(["wykladowca", "lecturer"]))
        .options(
            joinedload(User.teacher_profile),
            joinedload(User.departments_for_user).joinedload(DepartmentsForUser.department),
        )
    )

    if department_id is not None:
        query = query.join(
            DepartmentsForUser, DepartmentsForUser.user_id == User.user_id
        ).filter(DepartmentsForUser.department_id == department_id)

    users = query.order_by(User.last_name.asc(), User.first_name.asc()).all()

    result = []
    for user in users:
        teacher = user.teacher_profile
        dept_name = ""
        if user.departments_for_user:
            dept = user.departments_for_user[0].department
            dept_name = dept.name if dept else ""

        result.append({
            "user_id": user.user_id,
            "last_name": user.last_name,
            "first_name": user.first_name,
            "email": user.email,
            "title": teacher.title if teacher else "",
            "department_name": dept_name,
            "is_blocked": bool(getattr(user, "is_blocked", False)),
        })

    return result


def set_lecturer_blocked(db: Session, user_id: int, blocked: bool) -> User | None:
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        return None
    user.is_blocked = blocked
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_lecturer_data(
    db: Session,
    user_id: int,
    first_name: str,
    last_name: str,
    email: str,
    title: str | None = None,
    department_id: int | None = None,
) -> User | None:
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        return None

    user.first_name = first_name.strip()
    user.last_name = last_name.strip()
    user.email = email.strip().lower()

    # Update teacher title
    if title is not None:
        teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
        if teacher:
            teacher.title = title.strip()

    # Update DepartmentsForUser
    if department_id is not None:
        existing = (
            db.query(DepartmentsForUser)
            .filter(DepartmentsForUser.user_id == user_id)
            .all()
        )
        for dfu in existing:
            db.delete(dfu)
        db.add(DepartmentsForUser(user_id=user_id, department_id=department_id))

    db.commit()
    db.refresh(user)
    return user
