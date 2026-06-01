"""Shared pytest fixtures for API tests."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth.password_utils import hash_password
from app.core.database import SessionLocal
from app.cruds.crud_departments_for_user import add_department_to_user
from app.cruds.crud_role import get_role_by_name
from app.cruds.crud_roles_for_user import add_role_to_user
from app.cruds.crud_user import create_user, get_user_by_login
from app.main import fastapi_app
from app.models.model_department import Department
from app.models.model_role import Role
from app.seed_data.seed_model.seed_admin import seed_admin
from app.seed_data.seed_model.seed_departments import seed_departments
from app.seed_data.seed_model.seed_roles import seed_roles

TEST_ADMIN_LOGIN = "admin"
TEST_ADMIN_PASSWORD = "admin"
TEST_LECTURER_LOGIN = "test_lecturer"
TEST_LECTURER_PASSWORD = "lecturer"


def _ensure_roles_and_departments(db) -> None:
    if db.query(Role).first() is None:
        seed_departments(db)
        seed_roles(db)


def ensure_test_admin_user() -> None:
    """Ensure default admin exists (roles, departments, user). Idempotent."""
    db = SessionLocal()
    try:
        _ensure_roles_and_departments(db)
        if get_user_by_login(db, TEST_ADMIN_LOGIN) is not None:
            return
        seed_admin(db)
    finally:
        db.close()


def ensure_test_lecturer_user() -> None:
    """Ensure wykladowca test account exists. Idempotent."""
    db = SessionLocal()
    try:
        _ensure_roles_and_departments(db)
        existing = get_user_by_login(db, TEST_LECTURER_LOGIN)
        if existing is not None:
            if existing.email and existing.email.endswith(".local"):
                existing.email = "test.lecturer@example.com"
                db.commit()
            return

        lecturer_role = get_role_by_name(db, "wykladowca")
        department = db.query(Department).first()
        if lecturer_role is None or department is None:
            raise RuntimeError("Missing wykladowca role or department for test lecturer")

        user = create_user(
            db,
            first_name="Test",
            last_name="Lecturer",
            login=TEST_LECTURER_LOGIN,
            email="test.lecturer@example.com",
            password_hash=hash_password(TEST_LECTURER_PASSWORD),
            must_change_password=False,
        )
        add_role_to_user(db, int(user.user_id), int(lecturer_role.id))
        add_department_to_user(db, int(user.user_id), int(department.id))
    finally:
        db.close()


def _login(client: TestClient, login: str, password: str) -> TestClient:
    response = client.post("/auth/", json={"login": login, "password": password})
    assert response.status_code == 200, response.text
    return client


@pytest.fixture(scope="session")
def _seed_test_users_once() -> None:
    ensure_test_admin_user()
    ensure_test_lecturer_user()


@pytest.fixture
def db_session() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(_seed_test_users_once: None) -> TestClient:
    with TestClient(fastapi_app) as test_client:
        yield test_client


@pytest.fixture
def admin_client(_seed_test_users_once: None) -> TestClient:
    with TestClient(fastapi_app) as test_client:
        yield _login(test_client, TEST_ADMIN_LOGIN, TEST_ADMIN_PASSWORD)


@pytest.fixture
def lecturer_client(_seed_test_users_once: None) -> TestClient:
    with TestClient(fastapi_app) as test_client:
        yield _login(test_client, TEST_LECTURER_LOGIN, TEST_LECTURER_PASSWORD)
