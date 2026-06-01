"""JWT access-token checks on protected endpoints (cookie and Bearer)."""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from jose import jwt

from app.auth.jwt_utils import JWT_ALGORITHM, JWT_SECRET_KEY
from tests.conftest import TEST_ADMIN_LOGIN, TEST_ADMIN_PASSWORD

# Chroniony endpoint (w projekcie nie ma /api/users — jest /users/list)
PROTECTED_USERS_PATH = "/users/list"


def test_protected_users_without_token_returns_401(client: TestClient) -> None:
    response = client.get(PROTECTED_USERS_PATH)

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing access token"


def test_protected_users_with_invalid_bearer_returns_401(client: TestClient) -> None:
    response = client.get(
        PROTECTED_USERS_PATH,
        headers={"Authorization": "Bearer abc123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_protected_users_with_invalid_cookie_returns_401(client: TestClient) -> None:
    client.cookies.set("access_token", "not-a-valid-jwt")
    response = client.get(PROTECTED_USERS_PATH)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_expired_access_token_requires_new_login(client: TestClient) -> None:
    login = client.post(
        "/auth/",
        json={"login": TEST_ADMIN_LOGIN, "password": TEST_ADMIN_PASSWORD},
    )
    assert login.status_code == 200
    user_id = login.json()["user_id"]

    expired_token = jwt.encode(
        {
            "user_id": user_id,
            "roles": ["admin"],
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    client.cookies.set("access_token", expired_token)
    response = client.get(PROTECTED_USERS_PATH)

    assert response.status_code == 401
    assert response.json()["detail"] == "Access token expired"


def test_expired_bearer_token_requires_new_login(client: TestClient) -> None:
    login = client.post(
        "/auth/",
        json={"login": TEST_ADMIN_LOGIN, "password": TEST_ADMIN_PASSWORD},
    )
    assert login.status_code == 200
    user_id = login.json()["user_id"]

    expired_token = jwt.encode(
        {
            "user_id": user_id,
            "roles": ["admin"],
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    # Login ustawia ważne cookie — do testu Bearer używamy tylko nagłówka.
    client.cookies.clear()
    response = client.get(
        PROTECTED_USERS_PATH,
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Access token expired"
