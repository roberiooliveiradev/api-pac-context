"""Mapeamento operationId api-delpi → ctx_* (contrato GPT contexto operacional)."""

from __future__ import annotations

# Fase P1 — produto (playbook §8, itens 1–10).
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
}

PRODUCTS_API_PREFIX = "/products"
