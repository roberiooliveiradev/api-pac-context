"""Consolida respostas api-delpi de filiais 01 e 02 para o agente GPT."""

from __future__ import annotations

import copy
from typing import Any

from app.interface.http.route_contract_registry import ROUTE_CONTRACTS, resolve_contract

_LIST_KEYS = ("items", "records", "rows", "lines")


class CtxMultiBranchResponseMergeService:
    @classmethod
    def merge(cls, payloads: list[dict[str, Any]], operation_id: str) -> dict[str, Any]:
        if not payloads:
            return {"success": False, "message": "Sem respostas para consolidar.", "data": None}
        if len(payloads) == 1:
            return payloads[0]

        contract = ROUTE_CONTRACTS.get(str(operation_id or "").strip())
        shape = contract.shape if contract else resolve_contract(operation_id)[1]

        if shape in {"paged_list", "hierarchy", "playbook_report"}:
            return cls._merge_list_payloads(payloads)
        if shape == "composite_analysis":
            return cls._merge_composite_payloads(payloads)
        return cls._merge_list_payloads(payloads)

    @classmethod
    def is_empty_success_payload(cls, payload: dict[str, Any], operation_id: str) -> bool:
        if payload.get("success") is not True:
            return False
        contract = ROUTE_CONTRACTS.get(str(operation_id or "").strip())
        shape = contract.shape if contract else resolve_contract(operation_id)[1]
        data = payload.get("data")
        return cls._count_data_records(data, shape) == 0

    @classmethod
    def _count_data_records(cls, data: Any, shape: str) -> int:
        if data is None:
            return 0
        if shape in {"paged_list", "hierarchy"} and isinstance(data, dict):
            items = data.get("items")
            if isinstance(items, list):
                total = data.get("total")
                if isinstance(total, int):
                    return total
                return len(items)
        if shape == "playbook_report" and isinstance(data, dict):
            if isinstance(data.get("items"), list):
                return len(data["items"])
            total = 0
            for value in data.values():
                if isinstance(value, list):
                    total += len(value)
                elif isinstance(value, dict) and isinstance(value.get("items"), list):
                    total += len(value["items"])
            return total
        if shape == "composite_analysis" and isinstance(data, dict):
            return 1 if data else 0
        if isinstance(data, dict):
            return 1 if data else 0
        return 0

    @classmethod
    def _merge_list_payloads(cls, payloads: list[dict[str, Any]]) -> dict[str, Any]:
        base = copy.deepcopy(payloads[0])
        data = base.get("data")
        if not isinstance(data, dict):
            return base

        merged_items: list[Any] = []
        for payload in payloads:
            block = payload.get("data")
            if not isinstance(block, dict):
                continue
            items = block.get("items")
            if isinstance(items, list):
                merged_items.extend(items)
                continue
            for key in _LIST_KEYS:
                nested = block.get(key)
                if isinstance(nested, list):
                    merged_items.extend(nested)

        if merged_items or "items" in data:
            data["items"] = merged_items
            data["total"] = len(merged_items)
            data["page"] = 1
            data["page_size"] = len(merged_items) if merged_items else 0
            data["total_pages"] = 1 if merged_items else 0
            base["data"] = data

        return base

    @classmethod
    def _merge_composite_payloads(cls, payloads: list[dict[str, Any]]) -> dict[str, Any]:
        ranked = sorted(
            payloads,
            key=lambda payload: cls._count_data_records(
                payload.get("data"),
                "composite_analysis",
            ),
            reverse=True,
        )
        base = copy.deepcopy(ranked[0])
        base_data = base.get("data")
        if not isinstance(base_data, dict):
            return base

        for payload in ranked[1:]:
            other = payload.get("data")
            if not isinstance(other, dict):
                continue
            cls._merge_nested_lists(base_data, other)

        base["data"] = base_data
        return base

    @classmethod
    def _merge_nested_lists(cls, target: dict[str, Any], source: dict[str, Any]) -> None:
        for key, value in source.items():
            if isinstance(value, list) and value:
                existing = target.get(key)
                if isinstance(existing, list):
                    target[key] = [*existing, *value]
                else:
                    target[key] = list(value)
            elif isinstance(value, dict):
                current = target.get(key)
                if isinstance(current, dict):
                    cls._merge_nested_lists(current, value)
                elif key not in target or not target.get(key):
                    target[key] = copy.deepcopy(value)
