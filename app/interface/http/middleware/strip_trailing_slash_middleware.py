"""Remove barra final do path — evita redirect 307 que derruba Authorization no ChatGPT Actions."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import Response


async def strip_trailing_slash_middleware(request: Request, call_next) -> Response:
    path = request.scope.get("path", "")
    if path != "/" and path.endswith("/"):
        request.scope["path"] = path.rstrip("/")
    return await call_next(request)
