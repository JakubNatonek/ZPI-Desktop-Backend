"""Security response headers on HTTP API."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from app.core.security_headers import (
    ANTI_CLICKJACKING_HEADERS,
    SECURITY_HEADERS,
    SecurityHeadersASGIMiddleware,
)


async def _health(_: object) -> JSONResponse:
    return JSONResponse({"status": "ok"})


@pytest.fixture
def api_client() -> Iterator[TestClient]:
    app = Starlette(routes=[Route("/", _health)])
    app = SecurityHeadersASGIMiddleware(app)
    with TestClient(app) as test_client:
        yield test_client


def test_root_includes_content_security_policy(api_client: TestClient) -> None:
    response = api_client.get("/")

    assert response.status_code == 200
    csp = response.headers.get("content-security-policy")
    assert csp == SECURITY_HEADERS["Content-Security-Policy"]
    assert "default-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp


def test_root_includes_anti_clickjacking_headers(api_client: TestClient) -> None:
    response = api_client.get("/")

    assert response.headers.get("x-frame-options") == ANTI_CLICKJACKING_HEADERS["X-Frame-Options"]
    csp = response.headers.get("content-security-policy", "")
    assert "frame-ancestors 'none'" in csp


def test_root_includes_additional_security_headers(api_client: TestClient) -> None:
    response = api_client.get("/")

    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
