from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CtxAuthenticatedActor:
    id: str
    name: str
    email: str


_CTX_ACTOR: ContextVar[CtxAuthenticatedActor | None] = ContextVar(
    "ctx_authenticated_actor",
    default=None,
)

CTX_GPT_AGENT_ACTOR = CtxAuthenticatedActor(
    id="ctx-gpt-agent",
    name="Agente GPT Contexto PAC",
    email="ctx-gpt-agent@delpi.internal",
)


def set_ctx_authenticated_actor(actor: CtxAuthenticatedActor) -> Token:
    return _CTX_ACTOR.set(actor)


def reset_ctx_authenticated_actor(token: Token) -> None:
    _CTX_ACTOR.reset(token)


def clear_ctx_authenticated_actor() -> None:
    _CTX_ACTOR.set(None)


def get_ctx_authenticated_actor() -> CtxAuthenticatedActor | None:
    return _CTX_ACTOR.get()


def actor_as_request_user(actor: CtxAuthenticatedActor) -> Any:
    return actor
