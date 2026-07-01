"""Contratos semânticos (operationId → entity/shape) para meta / x-delpi."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RouteContract:
    entity: str
    shape: str


# Allowlist completa playbook §8 — 28 operações (P1 produto base + P2 PCP/qualidade).
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
        "ctx_get_product_stock",
        "ctx_get_product_internal_movements",
        "ctx_get_product_parents",
        "ctx_get_product_drawing",
        "ctx_get_production_order_by_op",
        "ctx_get_production_oee_appointment",
        "ctx_list_production_oee",
        "ctx_get_production_schedule_today",
        "ctx_get_production_orders_open",
        "ctx_get_production_orders_finished",
        "ctx_get_production_planned_vs_real",
        "ctx_get_production_losses_records",
        "ctx_get_production_losses_top_materials",
        "ctx_get_production_consumption_by_item",
        "ctx_list_nonconformities",
        "ctx_get_inspecoes_entrada_historico",
        "ctx_get_inspecoes_entrada_detalhe",
        "ctx_get_produced_quantity",
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
    "ctx_get_product_stock": RouteContract("product_stock", "paged_list"),
    "ctx_get_product_internal_movements": RouteContract(
        "product_internal_movements",
        "paged_list",
    ),
    "ctx_get_product_parents": RouteContract("product_parents", "hierarchy"),
    "ctx_get_product_drawing": RouteContract("product_drawing", "scalar"),
    "ctx_get_production_order_by_op": RouteContract(
        "production_order_detail",
        "playbook_report",
    ),
    "ctx_get_production_oee_appointment": RouteContract(
        "production_oee_appointment",
        "composite_analysis",
    ),
    "ctx_list_production_oee": RouteContract("production_oee_detail", "paged_list"),
    "ctx_get_production_schedule_today": RouteContract(
        "production_schedule_today",
        "playbook_report",
    ),
    "ctx_get_production_orders_open": RouteContract(
        "production_orders_open",
        "playbook_report",
    ),
    "ctx_get_production_orders_finished": RouteContract(
        "production_orders_finished",
        "playbook_report",
    ),
    "ctx_get_production_planned_vs_real": RouteContract(
        "production_planned_vs_real_time",
        "playbook_report",
    ),
    "ctx_get_production_losses_records": RouteContract(
        "production_losses_records",
        "playbook_report",
    ),
    "ctx_get_production_losses_top_materials": RouteContract(
        "production_losses_top_materials",
        "playbook_report",
    ),
    "ctx_get_production_consumption_by_item": RouteContract(
        "production_consumption_by_item",
        "playbook_report",
    ),
    "ctx_list_nonconformities": RouteContract("nonconformity", "paged_list"),
    "ctx_get_inspecoes_entrada_historico": RouteContract(
        "inspecoes_entrada_historico",
        "paged_list",
    ),
    "ctx_get_inspecoes_entrada_detalhe": RouteContract(
        "inspecoes_entrada_historico_detalhe",
        "object",
    ),
    "ctx_get_produced_quantity": RouteContract("produced_quantity", "playbook_report"),
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
