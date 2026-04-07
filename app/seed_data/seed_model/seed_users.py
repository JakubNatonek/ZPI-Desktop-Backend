from sqlalchemy.orm import Session

from app.auth.password_utils import hash_password
from app.models.model_department import Department
from app.models.model_role import Role
from app.models.model_user import User


def _validate_user_seed_payload(payload: dict) -> None:
    required_keys = [
        "first_name",
        "last_name",
        "album_number",
        "login",
        "email",
        "plain_password",
        "must_change_password",
        "public_key",
        "role_name",
        "department_name",
    ]
    missing = [key for key in required_keys if key not in payload]
    if missing:
        raise ValueError(f"User seed payload missing keys: {', '.join(missing)}")


def seed_users(db: Session) -> None:
    sample_users = [
        {
            "first_name": "admin",
            "last_name": "admin",
            "album_number": "admin",
            "login": "admin",
            "email": "admin@admin.admin",
            "plain_password": "admin",
            "must_change_password": False,
            "public_key": None,
            "role_name": "admin",
            "department_name": "Admin",
        },
        {
            "first_name": "test",
            "last_name": "test",
            "album_number": "test",
            "login": "test",
            "email": "test@test.test",
            "plain_password": "test",
            "must_change_password": False,
            "public_key": None,
            "role_name": "admin",
            "department_name": "Admin",
        },
    ]

    created = 0
    for user_payload in sample_users:
        _validate_user_seed_payload(user_payload)

        role = db.query(Role).filter(Role.name == user_payload["role_name"]).first()
        department = db.query(Department).filter(Department.name == user_payload["department_name"]).first()

        if role is None or department is None:
            print(
                "User seed skipped for "
                f"{user_payload['login']}: missing role={user_payload['role_name']} "
                f"or department={user_payload['department_name']}."
            )
            continue

        existing = db.query(User).filter(User.login == user_payload["login"]).first()
        if existing is not None:
            continue

        db.add(
            User(
                first_name=user_payload["first_name"],
                last_name=user_payload["last_name"],
                album_number=user_payload["album_number"],
                login=user_payload["login"],
                email=user_payload["email"],
                public_key=user_payload["public_key"],
                password_hash=hash_password(user_payload["plain_password"]),
                plain_password=user_payload["plain_password"],
                must_change_password=user_payload["must_change_password"],
                role_id=role.id,
                department_id=department.id,
            )
        )
        created += 1

    if created == 0:
        print("Users seeded: no new users added.")
        return

    db.commit()
    print(f"Users seeded: added {created} user(s).")