"""Mapeamento operationId api-delpi → ctx_* (contrato GPT contexto operacional)."""

from __future__ import annotations

# Playbook §8 — allowlist curada (28 operações).
DELPI_TO_CTX_OPERATION_ID: dict[str, str] = {
    "search_products": "ctx_search_products",
    "get_product_detail": "ctx_get_product_detail",
    "get_product_summary": "ctx_get_product_summary",
    "get_product_structure": "ctx_get_product_structure",
    "get_product_structure_exclusivity": "ctx_get_product_structure_exclusivity",
    "get_product_guide": "ctx_get_product_guide",
    "get_product_inspection": "ctx_get_product_inspection",
    "get_product_production_status": "ctx_get_product_production_status",
    "get_product_factory_status": "ctx_get_product_factory_status",
    "get_product_shipping_status": "ctx_get_product_shipping_status",
    "get_product_stock": "ctx_get_product_stock",
    "get_product_internal_movements": "ctx_get_product_internal_movements",
    "get_product_parents": "ctx_get_product_parents",
    "get_product_drawing": "ctx_get_product_drawing",
    "get_production_order_by_op": "ctx_get_production_order_by_op",
    "get_production_oee_appointment_by_id": "ctx_get_production_oee_appointment",
    "get_production_oee": "ctx_list_production_oee",
    "get_production_schedule_today": "ctx_get_production_schedule_today",
    "get_production_orders_open": "ctx_get_production_orders_open",
    "get_production_orders_finished": "ctx_get_production_orders_finished",
    "get_production_planned_vs_real_time": "ctx_get_production_planned_vs_real",
    "get_production_losses_records": "ctx_get_production_losses_records",
    "get_production_losses_top_materials": "ctx_get_production_losses_top_materials",
    "get_production_consumption_by_item": "ctx_get_production_consumption_by_item",
    "list_nonconformities": "ctx_list_nonconformities",
    "get_inspecoes_entrada_historico": "ctx_get_inspecoes_entrada_historico",
    "get_inspecoes_entrada_historico_detalhe": "ctx_get_inspecoes_entrada_detalhe",
    "get_produced_quantity": "ctx_get_produced_quantity",
}

PRODUCTS_API_PREFIX = "/products"
PRODUCTION_API_PREFIX = "/production"
QUALITY_API_PREFIX = "/quality"
INSPECOES_ENTRADA_API_PREFIX = "/inspecoes-entrada"
