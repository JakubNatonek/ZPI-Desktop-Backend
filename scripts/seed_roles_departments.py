from app.core.database import SessionLocal
from app.models.model_user import Role, Department
from sqlalchemy.orm import Session

def seed_roles_and_departments():
    db: Session = SessionLocal()
    try:
        # Departments
        departments = [
            {'id': 1, 'name': 'admin'},
            {'id': 2, 'name': 'Informatyka'},
            {'id': 3, 'name': 'Fizyka'},
        ]
        for dep in departments:
            exists = db.query(Department).filter_by(id=dep['id']).first()
            if not exists:
                db.add(Department(**dep))
        # Roles
        roles = [
            {'id': 1, 'name': 'admin'},
            {'id': 2, 'name': 'wykladowca'},
            {'id': 3, 'name': 'student'},
        ]
        for role in roles:
            exists = db.query(Role).filter_by(id=role['id']).first()
            if not exists:
                db.add(Role(**role))
        db.commit()
        print("Departments and roles seeded.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_roles_and_departments()
