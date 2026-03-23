from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.model_user import Department, Role, User
from app.seed_data.seed_departments import DzialEnum
from app.seed_data.seed_roles import RolaEnum


def seed_admin() -> None:
    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@admin.com").first()
        if admin:
            print("Admin user already exists.")
            return

        # Geting Admin Role
        role = db.query(Role).filter(Role.name == RolaEnum.ADMIN.value).first()
        #Geting Admin Department
        department = db.query(Department).filter(Department.name == DzialEnum.ADMIN.value).first()

        if role is None or department is None:
            raise RuntimeError("Missing admin role/department. Run seed_roles_and_departments first.")

        db.add(
            User(
                first_name="admin",
                last_name="admin",
                login="admin",
                email="admin@admin.com",
                password_hash="$2b$12$zi7AdboGsbPpUp4j3qFpv.WTir3I5odeMnqzyUW4DTaN956Jq3.p.",
                plain_password=None,
                must_change_password=False,
                role_id=role.id,
                department_id=department.id,
            )
        )
        db.commit()
        print("Admin user seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()