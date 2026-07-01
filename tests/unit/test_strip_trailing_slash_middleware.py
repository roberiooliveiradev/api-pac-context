"""Barra final não deve exigir redirect (ChatGPT Actions perde Bearer no 307)."""

from __future__ import annotations

import os
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.interface.http.middleware.ctx_auth_middleware import ctx_auth_middleware
from app.interface.http.middleware.strip_trailing_slash_middleware import (
    strip_trailing_slash_middleware,
)


def _build_test_app() -> FastAPI:
    app = FastAPI(redirect_slashes=False)
    app.middleware("http")(strip_trailing_slash_middleware)
    app.middleware("http")(ctx_auth_middleware)

    @app.get("/products/{code}/guide")
    def guide(code: str):
        return {"success": True, "code": code}

    return app


def test_trailing_slash_served_without_redirect():
    with patch.dict(os.environ, {"PAC_CONTEXT_API_KEY": "test-ctx-key"}, clear=False):
        client = TestClient(_build_test_app())
        response = client.get(
            "/products/90263382/guide/",
            headers={"Authorization": "Bearer test-ctx-key"},
        )
        assert response.status_code == 200
        assert response.json()["code"] == "90263382"
