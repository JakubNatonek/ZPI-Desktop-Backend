from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.model_department import Department
from app.models.model_department_for_user import DepartmentsForUser
from app.models.model_grade import GradeRecord
from app.models.model_group import Group
from app.models.model_role import Role
from app.models.model_role_for_user import RolesForUser
from app.models.model_student import Student
from app.models.model_user import User


def get_students_by_department(
    db: Session,
    department_id: int | None = None,
    studies_type: str | None = None,
    specialization_id: int | None = None,
    semester_id: int | None = None,
    album_query: str | None = None,
) -> list[dict]:
    """Return student records with user, group, department, and computed average grade."""
    query = (
        db.query(User)
        .join(RolesForUser, RolesForUser.user_id == User.user_id)
        .join(Role, RolesForUser.role_id == Role.id)
        .filter(func.lower(Role.name) == "student")
        .options(
            joinedload(User.student_profile).joinedload(Student.group).joinedload(Group.department),
            joinedload(User.departments_for_user).joinedload(DepartmentsForUser.department),
        )
    )

    has_student_join = False
    needs_group_join = bool(studies_type) or specialization_id is not None
    if needs_group_join:
        query = query.join(Student, Student.user_id == User.user_id).join(
            Group, Student.group_id == Group.id
        )
        has_student_join = True
        if studies_type:
            query = query.filter(func.lower(Group.studies_type) == studies_type.strip().lower())
        if specialization_id is not None:
            query = query.filter(Group.id == specialization_id)

    if department_id is not None:
        if needs_group_join:
            query = query.filter(Group.department_id == department_id)
        else:
            if not has_student_join:
                query = query.outerjoin(Student, Student.user_id == User.user_id)
                has_student_join = True

            query = (
                query
                .outerjoin(Group, Student.group_id == Group.id)
                .outerjoin(DepartmentsForUser, DepartmentsForUser.user_id == User.user_id)
                .filter(
                    or_(
                        Group.department_id == department_id,
                        DepartmentsForUser.department_id == department_id,
                    )
                )
            )

    if semester_id is not None:
        query = query.join(GradeRecord, GradeRecord.student_id == User.user_id).filter(
            GradeRecord.semester == semester_id,
            GradeRecord.is_final == True,  # noqa: E712
        )

    if album_query and album_query.strip():
        normalized_query = f"%{album_query.strip().lower()}%"
        if not has_student_join:
            query = query.outerjoin(Student, Student.user_id == User.user_id)
            has_student_join = True

        query = query.filter(
            or_(
                func.lower(User.album_number).like(normalized_query),
                func.lower(func.coalesce(Student.index_number, "")).like(normalized_query),
            )
        )

    users = query.distinct().order_by(User.last_name.asc(), User.first_name.asc()).all()

    result = []
    for user in users:
        student_profile = user.student_profile
        group = student_profile.group if student_profile else None
        department = group.department if group else None

        dept_id = None
        dept_name = ""
        if department:
            dept_id = department.id
            dept_name = department.name
        elif user.departments_for_user:
            dept_id = user.departments_for_user[0].department_id
            dept_name = user.departments_for_user[0].department.name if user.departments_for_user[0].department else ""

        specialization_id_value = group.id if group else None
        specialization_name = group.specialization if group else ""
        student_studies_type = group.studies_type if group else ""

        # Average from final grades
        avg_grade = (
            db.query(func.avg(GradeRecord.grade_value))
            .filter(
                GradeRecord.student_id == user.user_id,
                GradeRecord.is_final == True,  # noqa: E712
            )
            .scalar()
        )

        result.append({
            "user_id": user.user_id,
            "last_name": user.last_name,
            "first_name": user.first_name,
            "album_number": user.album_number,
            "email": user.email,
            "studies_type": student_studies_type or "",
            "average_grade": round(float(avg_grade), 2) if avg_grade else 0.0,
            "department_name": dept_name,
            "department_id": dept_id,
            "specialization_name": specialization_name,
            "specialization_id": specialization_id_value,
            "is_blocked": bool(getattr(user, "is_blocked", False)),
        })

    return result


def set_user_blocked(db: Session, user_id: int, blocked: bool) -> User | None:
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        return None
    user.is_blocked = blocked
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_student_data(
    db: Session,
    user_id: int,
    first_name: str,
    last_name: str,
    email: str,
    album_number: str,
    department_id: int | None = None,
    studies_type: str | None = None,
) -> User | None:
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        return None

    user.first_name = first_name.strip()
    user.last_name = last_name.strip()
    user.email = email.strip().lower()
    user.album_number = album_number.strip()

    # Update Group-level fields (department, studies_type) via Student profile
    student_profile = db.query(Student).filter(Student.user_id == user_id).first()
    if student_profile and student_profile.group_id:
        group = db.query(Group).filter(Group.id == student_profile.group_id).first()
        if group:
            if department_id is not None:
                group.department_id = department_id
            if studies_type is not None:
                group.studies_type = studies_type.strip()

    # Also keep DepartmentsForUser in sync
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
