"""Functional tests for /auth (login, me, logout)."""

from fastapi.testclient import TestClient

from tests.conftest import TEST_ADMIN_LOGIN, TEST_ADMIN_PASSWORD


def test_login_success_sets_cookies_and_returns_token(client: TestClient) -> None:
    response = client.post(
        "/auth/",
        json={"login": TEST_ADMIN_LOGIN, "password": TEST_ADMIN_PASSWORD},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["login"] == TEST_ADMIN_LOGIN
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["access_token_expires_in"] > 0
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


def test_login_invalid_password(client: TestClient) -> None:
    response = client.post(
        "/auth/",
        json={"login": TEST_ADMIN_LOGIN, "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid login or password"
    assert "access_token" not in response.cookies


def test_login_unknown_user(client: TestClient) -> None:
    response = client.post(
        "/auth/",
        json={"login": "no-such-user", "password": "any"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid login or password"


def test_me_requires_access_token_cookie(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing access token"


def test_me_after_login(client: TestClient) -> None:
    login = client.post(
        "/auth/",
        json={"login": TEST_ADMIN_LOGIN, "password": TEST_ADMIN_PASSWORD},
    )
    assert login.status_code == 200

    me = client.get("/auth/me")
    assert me.status_code == 200
    data = me.json()
    assert data["login"] == TEST_ADMIN_LOGIN
    assert data["user_id"] == login.json()["user_id"]


def test_logout_clears_auth_cookies(client: TestClient) -> None:
    client.post(
        "/auth/",
        json={"login": TEST_ADMIN_LOGIN, "password": TEST_ADMIN_PASSWORD},
    )

    logout = client.post("/auth/logout")
    assert logout.status_code == 200

    me = client.get("/auth/me")
    assert me.status_code == 401
