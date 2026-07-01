from __future__ import annotations

import logging
from typing import Any

from fastapi.responses import JSONResponse

from app.domain.services.ctx_agent_response_clarity_service import CtxAgentResponseClarityService
from app.domain.services.ctx_delpi_operation_mapping import DELPI_TO_CTX_OPERATION_ID
from app.domain.services.ctx_multi_branch_response_merge_service import (
    CtxMultiBranchResponseMergeService,
)
from app.domain.services import ctx_operational_branch_policy as branch_policy
from app.infrastructure.gateways.api_delpi_gateway import ApiDelpiGateway, ApiDelpiGatewayError

logger = logging.getLogger(__name__)


class CtxApiDelpiDelegationService:
    def __init__(self, gateway: ApiDelpiGateway | None = None) -> None:
        self._gateway = gateway or ApiDelpiGateway()

    def enabled(self) -> bool:
        return self._gateway.configured

    def _misconfigured_response(self) -> JSONResponse:
        agent_context = CtxAgentResponseClarityService.build_error_agent_context(
            error_code="API_DELPI_MISCONFIGURED",
            recoverable=False,
            interpretation_key="error.misconfigured",
        )
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
                "meta": {"agentContext": agent_context},
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

    def _enrich_for_agent(
        self,
        payload: dict[str, Any],
        ctx_operation_id: str,
        *,
        request_query: dict[str, Any] | None = None,
        branch_meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return CtxAgentResponseClarityService.enrich_success_payload(
            payload,
            ctx_operation_id,
            request_query=request_query,
            branch_meta=branch_meta,
        )

    def _resolve_path(self, path_prefix: str, path_suffix: str) -> str:
        prefix = path_prefix.rstrip("/")
        if not path_suffix:
            return prefix
        suffix = path_suffix if path_suffix.startswith("/") else f"/{path_suffix}"
        return f"{prefix}{suffix}"

    def _request_delpi_json(
        self,
        *,
        method: str,
        delpi_path: str,
        query: dict[str, Any] | None,
        json_body: Any,
    ) -> tuple[int, dict[str, Any] | Any]:
        return self._gateway.request_json(
            method,
            delpi_path,
            query=query,
            json_body=json_body,
        )

    def _collect_success_payloads(
        self,
        *,
        method: str,
        delpi_path: str,
        queries: list[dict[str, Any]],
        json_body: Any,
    ) -> tuple[int, list[dict[str, Any]]]:
        payloads: list[dict[str, Any]] = []
        last_status = 200
        for branch_query in queries:
            status, _headers, payload = self._request_delpi_json(
                method=method,
                delpi_path=delpi_path,
                query=branch_query,
                json_body=json_body,
            )
            last_status = status
            if isinstance(payload, dict) and payload.get("success") is True:
                payloads.append(payload)
        return last_status, payloads

    def _resolve_payload_with_branch_policy(
        self,
        *,
        method: str,
        delpi_path: str,
        ctx_operation_id: str,
        query: dict[str, Any] | None,
        json_body: Any,
    ) -> tuple[int, Any, dict[str, Any], dict[str, Any] | None]:
        branch_meta = {
            "consolidatedAcrossBranches": False,
            "branchFallbackApplied": False,
        }
        enrich_query: dict[str, Any] | None = query

        if branch_policy.should_consolidate_branches(ctx_operation_id, query):
            branch_meta["consolidatedAcrossBranches"] = True
            enrich_query = branch_policy.query_without_branch(query)
            status, payloads = self._collect_success_payloads(
                method=method,
                delpi_path=delpi_path,
                queries=branch_policy.branch_queries_for_consolidation(query),
                json_body=json_body,
            )
            if not payloads:
                status, _headers, payload = self._request_delpi_json(
                    method=method,
                    delpi_path=delpi_path,
                    query=enrich_query,
                    json_body=json_body,
                )
                return status, payload, branch_meta, enrich_query
            return status, CtxMultiBranchResponseMergeService.merge(payloads, ctx_operation_id), branch_meta, enrich_query

        status, _headers, payload = self._request_delpi_json(
            method=method,
            delpi_path=delpi_path,
            query=query,
            json_body=json_body,
        )

        if (
            isinstance(payload, dict)
            and branch_policy.should_retry_without_branch(
                ctx_operation_id,
                query,
                empty_result=CtxMultiBranchResponseMergeService.is_empty_success_payload(
                    payload,
                    ctx_operation_id,
                ),
                api_success=payload.get("success") is True,
            )
        ):
            fallback_query = branch_policy.query_without_branch(query)
            _status, fallback_payloads = self._collect_success_payloads(
                method=method,
                delpi_path=delpi_path,
                queries=branch_policy.branch_queries_for_consolidation(fallback_query),
                json_body=json_body,
            )
            merged = CtxMultiBranchResponseMergeService.merge(fallback_payloads, ctx_operation_id)
            if (
                fallback_payloads
                and not CtxMultiBranchResponseMergeService.is_empty_success_payload(
                    merged,
                    ctx_operation_id,
                )
            ):
                branch_meta["branchFallbackApplied"] = True
                branch_meta["consolidatedAcrossBranches"] = True
                enrich_query = fallback_query
                return 200, merged, branch_meta, enrich_query

        return status, payload, branch_meta, enrich_query

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
            status, payload, branch_meta, enrich_query = self._resolve_payload_with_branch_policy(
                method=method,
                delpi_path=delpi_path,
                ctx_operation_id=ctx_operation_id,
                query=query,
                json_body=json_body,
            )
        except ApiDelpiGatewayError as exc:
            code = exc.status_code or 503
            agent_context = CtxAgentResponseClarityService.build_error_agent_context(
                error_code="API_DELPI_UNAVAILABLE",
                recoverable=True,
                interpretation_key="error.gateway",
            )
            return JSONResponse(
                status_code=code,
                content={
                    "success": False,
                    "message": str(exc),
                    "data": None,
                    "error": {"code": "API_DELPI_UNAVAILABLE", "recoverable": True},
                    "meta": {"agentContext": agent_context},
                },
            )
        if isinstance(payload, dict):
            payload = self._rewrite_meta(payload, ctx_operation_id)
            payload = self._enrich_for_agent(
                payload,
                ctx_operation_id,
                request_query=enrich_query,
                branch_meta=branch_meta,
            )
            return JSONResponse(status_code=status, content=payload)
        agent_context = CtxAgentResponseClarityService.build_error_agent_context(
            error_code="API_DELPI_BAD_RESPONSE",
            recoverable=True,
            interpretation_key="error.bad_response",
        )
        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "message": "Resposta inválida da api-delpi.",
                "data": None,
                "error": {"code": "API_DELPI_BAD_RESPONSE", "recoverable": True},
                "meta": {"agentContext": agent_context},
            },
        )


_delegation_service: CtxApiDelpiDelegationService | None = None


def get_ctx_api_delpi_delegation_service() -> CtxApiDelpiDelegationService:
    global _delegation_service
    if _delegation_service is None:
        _delegation_service = CtxApiDelpiDelegationService()
    return _delegation_service
