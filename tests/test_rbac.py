"""Broad RBAC checks — admin-only vs authenticated vs forbidden roles."""

from fastapi.testclient import TestClient
import pytest

# Endpoints that require admin role
ADMIN_ONLY_READ = [
    ("GET", "/roles/list", None),
    ("GET", "/users/titles/list", None),
]
ADMIN_ONLY_WRITE = [
    ("POST", "/roles", {"name": "pytest_role_should_not_be_created"}),
    ("POST", "/departments", {"name": "Pytest Dept", "abbreviation": "PYT"}),
]
ADMIN_ONLY_ENDPOINTS = ADMIN_ONLY_READ + ADMIN_ONLY_WRITE

# Admin or rapla roles — plain wykladowca must not pass
RAPLA_OR_ADMIN_LIST_ENDPOINTS = [
    ("GET", "/departments/list", None),
    ("GET", "/room-types/list", None),
]

# Any logged-in user (get_current_user only)
AUTHENTICATED_ENDPOINTS = [
    ("GET", "/users/list", None),
]


def _request(client: TestClient, method: str, path: str, json_body: dict | None) -> int:
    if method == "GET":
        return client.get(path).status_code
    if method == "POST":
        return client.post(path, json=json_body or {}).status_code
    raise ValueError(f"Unsupported method: {method}")


@pytest.mark.parametrize("method,path,body", ADMIN_ONLY_ENDPOINTS)
def test_admin_only_endpoints_reject_lecturer(
    lecturer_client: TestClient,
    method: str,
    path: str,
    body: dict | None,
) -> None:
    assert _request(lecturer_client, method, path, body) == 403


@pytest.mark.parametrize("method,path,body", ADMIN_ONLY_READ)
def test_admin_only_read_endpoints_allow_admin(
    admin_client: TestClient,
    method: str,
    path: str,
    body: dict | None,
) -> None:
    assert _request(admin_client, method, path, body) == 200


@pytest.mark.parametrize("method,path,body", RAPLA_OR_ADMIN_LIST_ENDPOINTS)
def test_rapla_scoped_lists_reject_plain_lecturer(
    lecturer_client: TestClient,
    method: str,
    path: str,
    body: dict | None,
) -> None:
    assert _request(lecturer_client, method, path, body) == 403


@pytest.mark.parametrize("method,path,body", AUTHENTICATED_ENDPOINTS)
def test_authenticated_endpoints_reject_anonymous(
    client: TestClient,
    method: str,
    path: str,
    body: dict | None,
) -> None:
    assert _request(client, method, path, body) == 401


@pytest.mark.parametrize("method,path,body", AUTHENTICATED_ENDPOINTS)
def test_authenticated_endpoints_allow_lecturer(
    lecturer_client: TestClient,
    method: str,
    path: str,
    body: dict | None,
) -> None:
    assert _request(lecturer_client, method, path, body) == 200


def test_admin_only_post_users_create_rejects_lecturer(lecturer_client: TestClient) -> None:
    response = lecturer_client.post(
        "/users/create",
        json={
            "first_name": "Jan",
            "last_name": "Kowalski",
            "email": "jan.kowalski.pytest@test.local",
            "password": "password123",
            "role_ids": [1],
            "department_ids": [1],
        },
    )
    assert response.status_code == 403


def test_unauthenticated_cannot_list_roles(client: TestClient) -> None:
    assert client.get("/roles/list").status_code == 401
