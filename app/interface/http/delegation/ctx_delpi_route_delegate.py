from __future__ import annotations

from typing import Any

from app.core.actions_json_response import ActionsJSONResponse

from app.application.services.ctx_api_delpi_delegation_service import (
    get_ctx_api_delpi_delegation_service,
)


def delegate_json(
    *,
    method: str,
    path_prefix: str,
    path_suffix: str,
    ctx_operation_id: str,
    query: dict[str, Any] | None = None,
    json_body: Any = None,
) -> ActionsJSONResponse:
    return get_ctx_api_delpi_delegation_service().forward_json(
        method=method,
        path_prefix=path_prefix,
        path_suffix=path_suffix,
        ctx_operation_id=ctx_operation_id,
        query=query,
        json_body=json_body,
    )
