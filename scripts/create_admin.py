from app.core.database import SessionLocal
from app.models.model_user import User, RolaEnum, DzialEnum
from sqlalchemy.orm import Session

def create_admin():
    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@admin.com").first()
        if not admin:
            db.add(User(
                imie="admin",
                nazwisko="admin",
                login="admin",
                email="admin@admin.com",
                password_hash="$2b$12$zi7AdboGsbPpUp4j3qFpv.WTir3I5odeMnqzyUW4DTaN956Jq3.p.",
                plain_password=None,
                must_change_password=False,
                rola=RolaEnum.ADMIN,
                dzial=DzialEnum.ADMIN
            ))
            db.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
