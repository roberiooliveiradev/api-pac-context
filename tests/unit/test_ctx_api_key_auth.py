"""Autenticação PAC Context — PAC_CONTEXT_API_KEY."""

from __future__ import annotations

import os
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.interface.http.middleware.ctx_auth_middleware import ctx_auth_middleware


def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.middleware("http")(ctx_auth_middleware)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/products/search")
    def search():
        return {"success": True}

    return app


def test_public_health_without_api_key():
    client = TestClient(_build_test_app())
    response = client.get("/health")
    assert response.status_code == 200


def test_protected_route_requires_api_key():
    client = TestClient(_build_test_app())
    response = client.get("/products/search")
    assert response.status_code == 401
    assert response.json()["success"] is False


def test_protected_route_accepts_bearer_api_key():
    with patch.dict(os.environ, {"PAC_CONTEXT_API_KEY": "test-ctx-key"}, clear=False):
        client = TestClient(_build_test_app())
        response = client.get(
            "/products/search",
            headers={"Authorization": "Bearer test-ctx-key"},
        )
        assert response.status_code == 200


def test_protected_route_accepts_x_api_key_header():
    with patch.dict(os.environ, {"PAC_CONTEXT_API_KEY": "test-ctx-key"}, clear=False):
        client = TestClient(_build_test_app())
        response = client.get(
            "/products/search",
            headers={"X-Api-Key": "test-ctx-key"},
        )
        assert response.status_code == 200
