"""Contratos semânticos (operationId → entity/shape) para meta / x-delpi."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RouteContract:
    entity: str
    shape: str


# Fase P1 — produto (10 rotas). Meta completa §8 playbook: 28 ops (fase P2).
ANALYST_CONTEXT_OPERATION_IDS: frozenset[str] = frozenset(
    {
        "ctx_search_products",
        "ctx_get_product_detail",
        "ctx_get_product_summary",
        "ctx_get_product_structure",
        "ctx_get_product_structure_exclusivity",
        "ctx_get_product_guide",
        "ctx_get_product_inspection",
        "ctx_get_product_production_status",
        "ctx_get_product_factory_status",
        "ctx_get_product_shipping_status",
    }
)

CHATGPT_MAX_OPENAPI_OPERATIONS = 30

ROUTE_CONTRACTS: dict[str, RouteContract] = {
    "ctx_search_products": RouteContract("product_search", "paged_list"),
    "ctx_get_product_detail": RouteContract("product", "product_snapshot"),
    "ctx_get_product_summary": RouteContract("product", "product_snapshot"),
    "ctx_get_product_structure": RouteContract("product_structure", "hierarchy"),
    "ctx_get_product_structure_exclusivity": RouteContract(
        "product_structure_exclusivity",
        "playbook_report",
    ),
    "ctx_get_product_guide": RouteContract("product_guide", "paged_list"),
    "ctx_get_product_inspection": RouteContract("product_inspection", "paged_list"),
    "ctx_get_product_production_status": RouteContract(
        "product_production_status",
        "playbook_report",
    ),
    "ctx_get_product_factory_status": RouteContract(
        "product_factory_status",
        "composite_analysis",
    ),
    "ctx_get_product_shipping_status": RouteContract(
        "product_shipping_status",
        "playbook_report",
    ),
}


def default_entity(operation_id: str) -> str:
    token = str(operation_id or "").strip().lower()
    return token or "pac_context"


def resolve_contract(
    operation_id: str,
    *,
    entity: str | None = None,
    shape: str | None = None,
) -> tuple[str, str]:
    contract = ROUTE_CONTRACTS.get(str(operation_id or "").strip())
    resolved_entity = entity or (contract.entity if contract else default_entity(operation_id))
    resolved_shape = shape or (contract.shape if contract else "scalar")
    return resolved_entity, resolved_shape
