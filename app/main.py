from __future__ import annotations

import logging
import os

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.application.services.ctx_api_delpi_delegation_service import (
    get_ctx_api_delpi_delegation_service,
)
from app.config import settings
from app.core.responses import error_response, not_found_response
from app.interface.http.middleware.ctx_auth_middleware import ctx_auth_middleware
from app.interface.http.openapi_schema import build_openapi_schema
from app.interface.http.routes.context_products_router import router as products_router

logger = logging.getLogger(__name__)

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))


def build_allowed_origins() -> list[str]:
    origins: set[str] = set()
    public_base_url = os.getenv("PUBLIC_BASE_URL")
    if public_base_url:
        origins.add(public_base_url.rstrip("/"))
    if settings.API_ENV != "production":
        origins.update(
            {
                "http://localhost",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            }
        )
    return sorted(origins)


app = FastAPI(
    title="API PAC Context DELPI",
    description=(
        "BFF de leitura investigativa para o agente GPT — delega à api-delpi "
        "(produto, PCP, qualidade TOTVS). Somente GET."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=build_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(ctx_auth_middleware)
app.openapi = lambda: build_openapi_schema(app)
app.include_router(products_router)


@app.get("/health", include_in_schema=False)
def health():
    delegation = get_ctx_api_delpi_delegation_service()
    delegation_status = "configured" if delegation.enabled() else "misconfigured"
    status = "ok" if delegation.enabled() else "degraded"
    return {
        "status": status,
        "service": "api-pac-context",
        "api_delpi_delegation": delegation_status,
        "published_operations": 10,
        "phase": "P1-products",
    }


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return not_found_response(str(exc.detail))
    return error_response(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    return error_response(
        "Payload inválido.",
        status_code=422,
        code="VALIDATION_ERROR",
        meta={"details": jsonable_encoder(exc.errors())},
    )
