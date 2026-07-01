from __future__ import annotations

import logging

from fastapi import Request

from app.core.responses import error_response
from app.interface.http.middleware.ctx_api_key import request_has_valid_ctx_api_key
from app.interface.http.middleware.ctx_public_paths import is_public_path
from app.interface.http.middleware.ctx_request_context import (
    CTX_GPT_AGENT_ACTOR,
    actor_as_request_user,
    clear_ctx_authenticated_actor,
    reset_ctx_authenticated_actor,
    set_ctx_authenticated_actor,
)

logger = logging.getLogger(__name__)


async def ctx_auth_middleware(request: Request, call_next):
    """Autenticação única: `PAC_CONTEXT_API_KEY` (Bearer ou X-Api-Key)."""
    clear_ctx_authenticated_actor()

    path = request.url.path
    if is_public_path(path):
        return await call_next(request)

    if not request_has_valid_ctx_api_key(request):
        return error_response(
            "Não autorizado.",
            status_code=401,
            code="UNAUTHORIZED",
        )

    request.state.user = actor_as_request_user(CTX_GPT_AGENT_ACTOR)
    context_token = set_ctx_authenticated_actor(CTX_GPT_AGENT_ACTOR)

    try:
        return await call_next(request)
    except Exception:
        logger.exception("unhandled_error_ctx_api_key_request path=%s", path)
        return error_response(
            "Erro interno do servidor.",
            status_code=500,
            code="INTERNAL_ERROR",
        )
    finally:
        reset_ctx_authenticated_actor(context_token)
