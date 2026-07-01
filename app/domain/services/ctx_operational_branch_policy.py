"""Política de filial (01/02) para delegação GPT — consolidado vs. filial explícita."""

from __future__ import annotations

from typing import Any

OPERATIONAL_BRANCHES: tuple[str, ...] = ("01", "02")

# Rotas em que `branch` é obrigatório no contrato HTTP (não consolidar).
BRANCH_REQUIRED_OPERATIONS: frozenset[str] = frozenset(
    {
        "ctx_get_inspecoes_entrada_historico",
        "ctx_get_inspecoes_entrada_detalhe",
    }
)

# Rotas expostas ao GPT com parâmetro `branch` opcional.
BRANCH_OPTIONAL_OPERATIONS: frozenset[str] = frozenset(
    {
        "ctx_get_product_guide",
        "ctx_get_product_production_status",
        "ctx_get_product_factory_status",
        "ctx_get_product_shipping_status",
        "ctx_get_product_stock",
        "ctx_get_product_internal_movements",
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
        "ctx_get_produced_quantity",
    }
)


def _normalized_branch(query: dict[str, Any] | None) -> str | None:
    if not isinstance(query, dict):
        return None
    branch = query.get("branch")
    if branch is None:
        return None
    token = str(branch).strip()
    return token if len(token) == 2 else None


def supports_optional_branch(operation_id: str) -> bool:
    return str(operation_id or "").strip() in BRANCH_OPTIONAL_OPERATIONS


def branch_required(operation_id: str) -> bool:
    return str(operation_id or "").strip() in BRANCH_REQUIRED_OPERATIONS


def should_consolidate_branches(operation_id: str, query: dict[str, Any] | None) -> bool:
    """Sem filial informada → consultar e consolidar 01 + 02."""
    if branch_required(operation_id) or not supports_optional_branch(operation_id):
        return False
    return _normalized_branch(query) is None


def should_retry_without_branch(
    operation_id: str,
    query: dict[str, Any] | None,
    *,
    empty_result: bool,
    api_success: bool,
) -> bool:
    """Filial explícita retornou vazio → tentar consolidado 01+02."""
    if not supports_optional_branch(operation_id):
        return False
    if not api_success or not empty_result:
        return False
    return _normalized_branch(query) is not None


def query_without_branch(query: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(query, dict):
        return {}
    return {key: value for key, value in query.items() if key != "branch"}


def branch_queries_for_consolidation(query: dict[str, Any] | None) -> list[dict[str, Any]]:
    base = dict(query or {})
    base.pop("branch", None)
    return [{**base, "branch": branch} for branch in OPERATIONAL_BRANCHES]
