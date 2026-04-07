from sqlalchemy.orm import Session

from app.models.model_department import Department
from app.models.model_department_for_user import DepartmentsForUser
from app.models.model_user import User


def seed_departments_for_user(db: Session) -> None:
    user_ids = [row[0] for row in db.query(User.user_id).order_by(User.user_id.asc()).all()]
    department_ids = [row[0] for row in db.query(Department.id).order_by(Department.id.asc()).all()]

    if not user_ids or not department_ids:
        print("DepartmentsForUser skipped: missing users or departments.")
        return

    inserted = 0
    target_rows = 4

    for user_id in user_ids:
        for department_id in department_ids:
            if inserted >= target_rows:
                break

            exists = (
                db.query(DepartmentsForUser)
                .filter(
                    DepartmentsForUser.user_id == user_id,
                    DepartmentsForUser.department_id == department_id,
                )
                .first()
            )
            if exists is not None:
                continue

            db.add(DepartmentsForUser(user_id=user_id, department_id=department_id))
            inserted += 1

        if inserted >= target_rows:
            break

    if inserted == 0:
        print("DepartmentsForUser seeded: 0 new rows (all sample links already exist).")
        return

    db.commit()
    print(f"DepartmentsForUser seeded: added {inserted} rows.")