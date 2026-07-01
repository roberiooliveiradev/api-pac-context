"""Regressão: rotas de leitura devem enviar `page` default à api-delpi.

A api-delpi só aplica paginação quando `page` está presente; sem default a rota
retornava a lista inteira (ex.: parents = 414 registros / 58 KB), estourando o
limite de resposta do ChatGPT Actions ("Comunicação interrompida").
"""

from app.interface.http.openapi_schema import build_openapi_schema
from app.main import app

# operationId -> path com parâmetros de paginação obrigatoriamente com default
_PAGINATED_OPERATIONS = {
    "ctx_get_product_structure": "/products/{code}/structure",
    "ctx_get_product_guide": "/products/{code}/guide",
    "ctx_get_product_inspection": "/products/{code}/inspection",
    "ctx_get_product_parents": "/products/{code}/parents",
}


def _param(operation: dict, name: str) -> dict:
    for param in operation.get("parameters", []):
        if param.get("name") == name:
            return param
    raise AssertionError(f"parâmetro {name} ausente")


def test_read_routes_default_page_to_one():
    schema = build_openapi_schema(app)
    paths = schema.get("paths") or {}

    for operation_id, path in _PAGINATED_OPERATIONS.items():
        operation = paths.get(path, {}).get("get", {})
        assert operation.get("operationId") == operation_id

        page = _param(operation, "page")
        page_size = _param(operation, "page_size")

        assert page["schema"].get("default") == 1, (
            f"{operation_id}: `page` precisa de default 1 para a api-delpi paginar"
        )
        assert page_size["schema"].get("default") == 50, (
            f"{operation_id}: `page_size` precisa de default para limitar a resposta"
        )
