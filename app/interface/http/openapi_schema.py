from __future__ import annotations

import os

from fastapi.openapi.utils import get_openapi

CTX_API_KEY_SECURITY_SCHEME = {
    "CtxApiKey": {
        "type": "http",
        "scheme": "bearer",
        "description": "PAC_CONTEXT_API_KEY — Authorization: Bearer <token>",
    }
}


def build_openapi_schema(app):
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    components = schema.setdefault("components", {})
    components["securitySchemes"] = CTX_API_KEY_SECURITY_SCHEME
    schema["security"] = [{"CtxApiKey": []}]

    public_base_url = (os.getenv("PUBLIC_BASE_URL") or "").strip().rstrip("/")
    if public_base_url:
        schema["servers"] = [{"url": public_base_url, "description": "API PAC Context"}]

    from app.interface.http.openapi_delpi_extension_injector import inject_delpi_extensions

    inject_delpi_extensions(schema)

    health_path = schema.get("paths", {}).get("/health")
    if isinstance(health_path, dict):
        for operation in health_path.values():
            if isinstance(operation, dict):
                operation["security"] = []

    app.openapi_schema = schema
    return schema
