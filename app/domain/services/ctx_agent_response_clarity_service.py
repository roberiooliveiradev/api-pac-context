from __future__ import annotations

from typing import Any

from app.domain.services.ctx_agent_response_content_service import CtxAgentResponseContentService
from app.interface.http.route_contract_registry import ROUTE_CONTRACTS, resolve_contract

_LIST_KEYS = ("items", "records", "rows", "lines", "nodes", "children")
_COMPOSITE_SIGNAL_KEYS = (
    "factory_status",
    "summary",
    "indicators",
    "product",
    "reference_date",
    "appointments",
    "orders",
    "production",
    "shipping",
    "structure",
)


class CtxAgentResponseClarityService:
    @classmethod
    def enrich_success_payload(cls, payload: dict[str, Any], operation_id: str) -> dict[str, Any]:
        if not isinstance(payload, dict):
            return payload

        contract = ROUTE_CONTRACTS.get(str(operation_id or "").strip())
        entity, shape = resolve_contract(
            operation_id,
            entity=contract.entity if contract else None,
            shape=contract.shape if contract else None,
        )

        payload = cls._normalize_data(payload, shape)
        agent_context = cls._build_agent_context(payload, operation_id, shape, entity)

        meta = payload.get("meta")
        if not isinstance(meta, dict):
            meta = {}
        payload = {**payload, "meta": {**meta, "agentContext": agent_context}}
        return cls._sync_meta_pagination(payload)

    @classmethod
    def _sync_meta_pagination(cls, payload: dict[str, Any]) -> dict[str, Any]:
        data = payload.get("data")
        if not isinstance(data, dict):
            return payload
        page = data.get("page")
        page_size = data.get("page_size")
        total = data.get("total")
        total_pages = data.get("total_pages")
        if page is None and page_size is None:
            return payload

        meta = payload.get("meta")
        if not isinstance(meta, dict):
            return payload
        pagination = meta.get("pagination")
        if not isinstance(pagination, dict):
            return payload

        return {
            **payload,
            "meta": {
                **meta,
                "pagination": {
                    **pagination,
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                },
            },
        }

    @classmethod
    def build_error_agent_context(
        cls,
        *,
        error_code: str,
        recoverable: bool,
        interpretation_key: str,
    ) -> dict[str, Any]:
        return {
            "queryStatus": "error",
            "hasData": False,
            "emptyResult": False,
            "recordCount": 0,
            "apiSuccess": False,
            "errorCode": error_code,
            "recoverable": recoverable,
            "interpretation": CtxAgentResponseContentService.interpretation(interpretation_key),
        }

    @classmethod
    def _normalize_data(cls, payload: dict[str, Any], shape: str) -> dict[str, Any]:
        data = payload.get("data")
        if not isinstance(data, dict):
            return payload

        if "items" in data and isinstance(data.get("items"), list):
            return {**payload, "data": cls._normalize_paged_block(data)}

        if shape in {"hierarchy", "playbook_report", "composite_analysis"}:
            normalized = dict(data)
            for key, value in data.items():
                if isinstance(value, dict) and "items" in value:
                    normalized[key] = cls._normalize_paged_block(value)
            if normalized != data:
                return {**payload, "data": normalized}

        return payload

    @staticmethod
    def _normalize_paged_block(block: dict[str, Any]) -> dict[str, Any]:
        items = block.get("items")
        if not isinstance(items, list):
            return block

        total = block.get("total")
        if total is None:
            total = len(items)

        page = block.get("page") if block.get("page") is not None else 1
        page_size = block.get("page_size")
        if page_size is None:
            page_size = len(items) if items else 0

        total_pages = block.get("total_pages")
        if total_pages is None:
            if total == 0 or page_size == 0:
                total_pages = 0
            else:
                total_pages = (int(total) + int(page_size) - 1) // int(page_size)

        return {
            **block,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        }

    @classmethod
    def _build_agent_context(
        cls,
        payload: dict[str, Any],
        operation_id: str,
        shape: str,
        entity: str,
    ) -> dict[str, Any]:
        data = payload.get("data")
        record_count = cls._count_records(data, shape)
        query_status = cls._resolve_query_status(data, shape, record_count)
        interpretation = cls._resolve_interpretation(
            operation_id,
            shape,
            query_status,
            record_count,
        )

        return {
            "queryStatus": query_status,
            "hasData": query_status == "ok",
            "emptyResult": query_status in {"empty", "not_found"},
            "recordCount": record_count,
            "shape": shape,
            "entity": entity,
            "operationId": operation_id,
            "interpretation": interpretation,
            "apiSuccess": payload.get("success") is True,
        }

    @classmethod
    def _resolve_query_status(
        cls,
        data: Any,
        shape: str,
        record_count: int,
    ) -> str:
        if shape == "scalar" and isinstance(data, dict) and data.get("found") is False:
            return "not_found"
        if shape == "product_snapshot" and record_count == 0:
            return "not_found"
        if record_count == 0:
            return "empty"
        return "ok"

    @classmethod
    def _resolve_interpretation(
        cls,
        operation_id: str,
        shape: str,
        query_status: str,
        record_count: int,
    ) -> str:
        if query_status in {"empty", "not_found"}:
            operation_hint = CtxAgentResponseContentService.operation_empty_hint(operation_id)
            if operation_hint:
                return operation_hint

        status_key = query_status if query_status != "not_found" else "not_found"
        if shape == "scalar" and query_status == "empty":
            status_key = "empty"
        elif query_status == "ok":
            status_key = "ok"

        template_key = f"{shape}.{status_key}"
        interpretation = CtxAgentResponseContentService.interpretation(
            template_key,
            record_count=record_count,
        )
        if interpretation:
            return interpretation

        fallback_key = "paged_list.empty" if query_status != "ok" else "paged_list.ok"
        return CtxAgentResponseContentService.interpretation(
            fallback_key,
            record_count=record_count,
        )

    @classmethod
    def _count_records(cls, data: Any, shape: str) -> int:
        if data is None:
            return 0
        if shape == "paged_list":
            return cls._count_list_block(data)
        if shape == "hierarchy":
            return cls._count_list_block(data)
        if shape == "playbook_report":
            return cls._count_playbook_report(data)
        if shape == "composite_analysis":
            return cls._count_composite_analysis(data)
        if shape == "product_snapshot":
            return cls._count_product_snapshot(data)
        if shape == "scalar":
            return cls._count_scalar(data)
        if shape == "object":
            return 1 if isinstance(data, dict) and bool(data) else 0
        if isinstance(data, list):
            return len(data)
        if isinstance(data, dict):
            return 1 if data else 0
        return 1

    @classmethod
    def _count_list_block(cls, data: Any) -> int:
        if not isinstance(data, dict):
            return 0
        items = data.get("items")
        if isinstance(items, list):
            total = data.get("total")
            if isinstance(total, int):
                return total
            return len(items)
        return 0

    @classmethod
    def _count_playbook_report(cls, data: Any) -> int:
        if not isinstance(data, dict):
            return 0
        if isinstance(data.get("items"), list):
            return cls._count_list_block(data)
        total = 0
        for value in data.values():
            if isinstance(value, list) and value:
                total += len(value)
            elif isinstance(value, dict):
                total += cls._count_nested_items(value)
        return total

    @classmethod
    def _count_composite_analysis(cls, data: Any) -> int:
        if not isinstance(data, dict) or not data:
            return 0
        if any(data.get(key) for key in _COMPOSITE_SIGNAL_KEYS):
            nested = cls._count_nested_items(data)
            return max(1, nested)
        return cls._count_nested_items(data)

    @classmethod
    def _count_nested_items(cls, block: dict[str, Any], *, depth: int = 0) -> int:
        if depth > 2:
            return 0
        total = 0
        for key in _LIST_KEYS:
            value = block.get(key)
            if isinstance(value, list):
                total += len(value)
        for value in block.values():
            if isinstance(value, dict):
                total += cls._count_nested_items(value, depth=depth + 1)
        return total

    @staticmethod
    def _count_product_snapshot(data: Any) -> int:
        if not isinstance(data, dict):
            return 0
        product = data.get("product")
        if isinstance(product, dict):
            if product.get("product_code") or product.get("code"):
                return 1
            return 0
        if data.get("product_code") or data.get("code"):
            return 1
        return 1 if data else 0

    @staticmethod
    def _count_scalar(data: Any) -> int:
        if not isinstance(data, dict):
            return 0 if data in {None, ""} else 1
        if data.get("found") is False:
            return 0
        if data.get("found") is True:
            return 1
        return 1 if data else 0
