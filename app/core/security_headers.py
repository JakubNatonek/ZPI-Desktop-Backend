"""HTTP security headers for API and ASGI (incl. Socket.IO) responses."""

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

# JSON API — no HTML/scripts; blocks embedding in frames.
API_CONTENT_SECURITY_POLICY = (
    "default-src 'none'; "
    "base-uri 'none'; "
    "form-action 'none'; "
    "frame-ancestors 'none'; "
    "object-src 'none'"
)

# Anti-clickjacking: legacy header + CSP (OWASP recommends both for compatibility).
ANTI_CLICKJACKING_HEADERS: dict[str, str] = {
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": API_CONTENT_SECURITY_POLICY,
}

SECURITY_HEADERS: dict[str, str] = {
    **ANTI_CLICKJACKING_HEADERS,
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


def _has_header(headers: list[tuple[bytes, bytes]], name: str) -> bool:
    name_lower = name.lower().encode()
    return any(key.lower() == name_lower for key, _ in headers)


def _apply_security_headers(headers: list[tuple[bytes, bytes]]) -> list[tuple[bytes, bytes]]:
    updated = list(headers)
    for name, value in SECURITY_HEADERS.items():
        if not _has_header(updated, name):
            updated.append((name.lower().encode("latin-1"), value.encode("latin-1")))
    return updated


class SecurityHeadersASGIMiddleware:
    """Apply security headers to every HTTP response (FastAPI, Socket.IO, static)."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_security_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                message = {
                    **message,
                    "headers": _apply_security_headers(list(message.get("headers", []))),
                }
            await send(message)

        await self.app(scope, receive, send_with_security_headers)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        for name, value in SECURITY_HEADERS.items():
            if name not in response.headers:
                response.headers[name] = value
        return response
