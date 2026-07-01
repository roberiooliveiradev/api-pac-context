from __future__ import annotations

import logging
import time

from fastapi import Request

logger = logging.getLogger("ctx.request")


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "-"


def _auth_kind(request: Request) -> str:
    authorization = request.headers.get("authorization")
    if authorization:
        scheme = authorization.split(" ", 1)[0].lower() if " " in authorization else "raw"
        return f"authorization:{scheme}"
    if request.headers.get("x-api-key"):
        return "x-api-key"
    return "none"


async def request_logging_middleware(request: Request, call_next):
    """Log detalhado de cada request: origem, credencial, status e latência.

    Externo a todos os middlewares (inclusive auth) para registrar também 401/403.
    """
    started = time.perf_counter()
    method = request.method
    path = request.url.path
    query = request.url.query
    ip = _client_ip(request)
    user_agent = request.headers.get("user-agent", "-")
    auth_kind = _auth_kind(request)

    logger.info(
        "req.in method=%s path=%s query=%s ip=%s auth=%s ua=%r",
        method,
        path,
        query or "-",
        ip,
        auth_kind,
        user_agent,
    )

    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.exception(
            "req.error method=%s path=%s ip=%s auth=%s ua=%r elapsed_ms=%.1f",
            method,
            path,
            ip,
            auth_kind,
            user_agent,
            elapsed_ms,
        )
        raise

    elapsed_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "req.out method=%s path=%s status=%s ip=%s auth=%s ua=%r elapsed_ms=%.1f",
        method,
        path,
        response.status_code,
        ip,
        auth_kind,
        user_agent,
        elapsed_ms,
    )
    return response
