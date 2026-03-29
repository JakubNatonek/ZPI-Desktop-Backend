from app.core.database import SessionLocal
from app.models.model_user import User
from sqlalchemy.orm import Session

def create_admin():
    db: Session = SessionLocal()
    try:
        default_password_hash = "$2b$12$WBVbY5qn9EMmPJHCzTY1JenHu7vFrRC/NQn.8XSy8k2OEtPRvS8lO"

        admin = db.query(User).filter(User.email == "admin@admin.com").first()
        if not admin:
            db.add(User(
                first_name="admin",
                last_name="admin",
                login="admin",
                email="admin@admin.com",
                password_hash=default_password_hash,
                plain_password=None,
                must_change_password=False,
                role_id=1,
                department_id=1 
            ))
            print("Admin user created.")
        else:
            print("Admin user already exists.")

        student = db.query(User).filter(User.login == "stu").first()
        if not student:
            db.add(User(
                first_name="student",
                last_name="student",
                login="stu",
                email="student@student.com",
                password_hash=default_password_hash,
                plain_password=None,
                must_change_password=False,
                role_id=3,
                department_id=1
            ))
            print("Student user created.")
        else:
            print("Student user already exists.")

        wykladowca = db.query(User).filter(User.login == "wyk").first()
        if not wykladowca:
            db.add(User(
                first_name="wykladowca",
                last_name="wykladowca",
                login="wyk",
                email="wykladowca@wykladowca.com",
                password_hash=default_password_hash,
                plain_password=None,
                must_change_password=False,
                role_id=2,
                department_id=1
            ))
            print("Wykladowca user created.")
        else:
            print("Wykladowca user already exists.")

        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
