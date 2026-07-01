from app.interface.http.openapi_schema import build_openapi_schema
from app.interface.http.route_contract_registry import (
    ANALYST_CONTEXT_OPERATION_IDS,
    CHATGPT_MAX_OPENAPI_OPERATIONS,
    ROUTE_CONTRACTS,
)
from app.main import app


def _published_operation_ids(schema: dict) -> set[str]:
    rows: set[str] = set()
    for path_item in (schema.get("paths") or {}).values():
        if not isinstance(path_item, dict):
            continue
        for operation in path_item.values():
            if isinstance(operation, dict):
                op_id = str(operation.get("operationId") or "").strip()
                if op_id:
                    rows.add(op_id)
    return rows


def test_registry_matches_allowlist():
    assert frozenset(ROUTE_CONTRACTS) == ANALYST_CONTEXT_OPERATION_IDS


def test_openapi_exposes_only_analyst_operations():
    schema = build_openapi_schema(app)
    published = _published_operation_ids(schema)
    assert published == ANALYST_CONTEXT_OPERATION_IDS
    assert len(published) <= CHATGPT_MAX_OPENAPI_OPERATIONS
    assert "/health" not in schema.get("paths", {})


def test_openapi_injects_x_delpi_extensions():
    schema = build_openapi_schema(app)
    paths = schema.get("paths") or {}
    structure_op = paths.get("/products/{code}/structure", {}).get("get", {})
    assert structure_op.get("operationId") == "ctx_get_product_structure"
    assert structure_op.get("x-delpi", {}).get("entity") == "product_structure"
