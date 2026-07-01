"""Normaliza query params enviados vazios por clientes Actions (ex.: ChatGPT)."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode

from starlette.requests import Request
from starlette.responses import Response

_BLANK_QUERY_VALUES = frozenset({"", "null", "undefined"})


def _should_drop_query_value(value: str) -> bool:
    return value.strip().lower() in _BLANK_QUERY_VALUES


async def normalize_query_params_middleware(
    request: Request,
    call_next,
) -> Response:
    query_string = request.scope.get("query_string", b"")
    if query_string:
        pairs = parse_qsl(query_string.decode(), keep_blank_values=True)
        cleaned = [
            (key, value)
            for key, value in pairs
            if not _should_drop_query_value(value)
        ]
        if len(cleaned) != len(pairs):
            request.scope["query_string"] = urlencode(cleaned, doseq=True).encode()
    return await call_next(request)
