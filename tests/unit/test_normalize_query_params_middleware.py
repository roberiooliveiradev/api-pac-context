"""Query params vazios ou literais 'null' devem ser omitidos antes da validação FastAPI."""

from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.testclient import TestClient

from app.interface.http.middleware.normalize_query_params_middleware import (
    normalize_query_params_middleware,
)


def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.middleware("http")(normalize_query_params_middleware)

    @app.get("/guide")
    def guide(
        branch: str | None = Query(default=None, min_length=2, max_length=2),
        page: int | None = Query(default=None, ge=1),
    ):
        return {"branch": branch, "page": page}

    return app


def test_empty_branch_query_param_is_omitted():
    client = TestClient(_build_test_app())
    response = client.get("/guide?branch=")
    assert response.status_code == 200
    assert response.json() == {"branch": None, "page": None}


def test_literal_null_branch_query_param_is_omitted():
    client = TestClient(_build_test_app())
    response = client.get("/guide?branch=null")
    assert response.status_code == 200
    assert response.json() == {"branch": None, "page": None}


def test_empty_page_query_param_is_omitted():
    client = TestClient(_build_test_app())
    response = client.get("/guide?page=")
    assert response.status_code == 200
    assert response.json() == {"branch": None, "page": None}


def test_valid_branch_query_param_is_preserved():
    client = TestClient(_build_test_app())
    response = client.get("/guide?branch=02")
    assert response.status_code == 200
    assert response.json() == {"branch": "02", "page": None}
