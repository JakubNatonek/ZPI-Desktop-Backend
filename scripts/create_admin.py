from app.core.database import SessionLocal
from app.models.model_user import User
from sqlalchemy.orm import Session

def create_admin():
    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@admin.com").first()
        if not admin:
            db.add(User(
                first_name="admin",
                last_name="admin",
                album_number="00001",
                login="admin",
                email="admin@admin.com",
                password_hash="$2b$12$zi7AdboGsbPpUp4j3qFpv.WTir3I5odeMnqzyUW4DTaN956Jq3.p.",
                plain_password=None,
                must_change_password=False,
                role_id=1,
                department_id=1 
            ))
            db.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
