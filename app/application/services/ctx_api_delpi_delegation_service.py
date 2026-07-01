from __future__ import annotations

import logging
from typing import Any

from fastapi.responses import JSONResponse

from app.domain.services.ctx_delpi_operation_mapping import DELPI_TO_CTX_OPERATION_ID
from app.infrastructure.gateways.api_delpi_gateway import ApiDelpiGateway, ApiDelpiGatewayError

logger = logging.getLogger(__name__)


class CtxApiDelpiDelegationService:
    def __init__(self, gateway: ApiDelpiGateway | None = None) -> None:
        self._gateway = gateway or ApiDelpiGateway()

    def enabled(self) -> bool:
        return self._gateway.configured

    def _misconfigured_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "message": (
                    "Delegação para api-delpi não configurada. "
                    "Defina API_DELPI_BASE_URL e API_DELPI_INTERNAL_SERVICE_TOKEN."
                ),
                "data": None,
                "error": {"code": "API_DELPI_MISCONFIGURED", "recoverable": False},
            },
        )

    def _rewrite_meta(self, payload: dict[str, Any], ctx_operation_id: str) -> dict[str, Any]:
        if not isinstance(payload, dict):
            return payload
        meta = payload.get("meta")
        if isinstance(meta, dict):
            delpi_op = meta.get("operationId")
            if isinstance(delpi_op, str) and delpi_op in DELPI_TO_CTX_OPERATION_ID:
                meta = {**meta, "operationId": DELPI_TO_CTX_OPERATION_ID[delpi_op]}
            else:
                meta = {**meta, "operationId": ctx_operation_id}
            payload = {**payload, "meta": meta}
        return payload

    def _normalize_paged_list_null_pagination(self, payload: dict[str, Any]) -> dict[str, Any]:
        """api-delpi devolve page/page_size null em listas vazias — ChatGPT Actions falha na validação."""
        data = payload.get("data")
        if not isinstance(data, dict) or "items" not in data:
            return payload

        items = data.get("items")
        if not isinstance(items, list):
            return payload

        total = data.get("total")
        if total is None:
            total = len(items)

        page = data.get("page") if data.get("page") is not None else 1
        page_size = data.get("page_size")
        if page_size is None:
            page_size = len(items) if items else 0

        total_pages = data.get("total_pages")
        if total_pages is None:
            if total == 0 or page_size == 0:
                total_pages = 0
            else:
                total_pages = (int(total) + int(page_size) - 1) // int(page_size)

        normalized_data = {
            **data,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        }
        payload = {**payload, "data": normalized_data}

        meta = payload.get("meta")
        if isinstance(meta, dict) and isinstance(meta.get("pagination"), dict):
            pagination = {
                **meta["pagination"],
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
            }
            payload = {**payload, "meta": {**meta, "pagination": pagination}}

        return payload

    def _resolve_path(self, path_prefix: str, path_suffix: str) -> str:
        prefix = path_prefix.rstrip("/")
        if not path_suffix:
            return prefix
        suffix = path_suffix if path_suffix.startswith("/") else f"/{path_suffix}"
        return f"{prefix}{suffix}"

    def forward_json(
        self,
        *,
        method: str,
        path_prefix: str,
        path_suffix: str,
        ctx_operation_id: str,
        query: dict[str, Any] | None = None,
        json_body: Any = None,
    ) -> JSONResponse:
        if not self.enabled():
            return self._misconfigured_response()
        delpi_path = self._resolve_path(path_prefix, path_suffix)
        try:
            status, _headers, payload = self._gateway.request_json(
                method,
                delpi_path,
                query=query,
                json_body=json_body,
            )
        except ApiDelpiGatewayError as exc:
            code = exc.status_code or 503
            return JSONResponse(
                status_code=code,
                content={
                    "success": False,
                    "message": str(exc),
                    "data": None,
                    "error": {"code": "API_DELPI_UNAVAILABLE", "recoverable": True},
                },
            )
        if isinstance(payload, dict):
            payload = self._rewrite_meta(payload, ctx_operation_id)
            payload = self._normalize_paged_list_null_pagination(payload)
            return JSONResponse(status_code=status, content=payload)
        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "message": "Resposta inválida da api-delpi.",
                "data": None,
                "error": {"code": "API_DELPI_BAD_RESPONSE", "recoverable": True},
            },
        )


_delegation_service: CtxApiDelpiDelegationService | None = None


def get_ctx_api_delpi_delegation_service() -> CtxApiDelpiDelegationService:
    global _delegation_service
    if _delegation_service is None:
        _delegation_service = CtxApiDelpiDelegationService()
    return _delegation_service
