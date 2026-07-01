from __future__ import annotations

from unittest.mock import MagicMock

from app.application.services.ctx_api_delpi_delegation_service import CtxApiDelpiDelegationService
from app.domain.services.ctx_delpi_operation_mapping import DELPI_TO_CTX_OPERATION_ID, PRODUCTS_API_PREFIX


def test_delegation_misconfigured_without_gateway():
    gateway = MagicMock()
    gateway.configured = False
    service = CtxApiDelpiDelegationService(gateway=gateway)
    response = service.forward_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix="/search",
        ctx_operation_id="ctx_search_products",
    )
    assert response.status_code == 503
    gateway.request_json.assert_not_called()


def test_delegation_rewrites_operation_id():
    gateway = MagicMock()
    gateway.configured = True
    gateway.request_json.return_value = (
        200,
        {},
        {
            "success": True,
            "data": {},
            "meta": {"operationId": "get_product_structure", "entity": "product_structure"},
        },
    )
    service = CtxApiDelpiDelegationService(gateway=gateway)
    response = service.forward_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix="/10156007/structure",
        ctx_operation_id="ctx_get_product_structure",
    )
    assert response.status_code == 200
    body = response.body.decode()
    assert "ctx_get_product_structure" in body
    gateway.request_json.assert_called_once_with(
        "GET",
        "/products/10156007/structure",
        query=None,
        json_body=None,
    )


def test_delpi_to_ctx_mapping_keys():
    assert DELPI_TO_CTX_OPERATION_ID["get_product_production_status"] == (
        "ctx_get_product_production_status"
    )
