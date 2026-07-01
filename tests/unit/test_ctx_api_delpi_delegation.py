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
    assert len(DELPI_TO_CTX_OPERATION_ID) == 28


def test_delegation_normalizes_null_pagination_for_paged_list():
    gateway = MagicMock()
    gateway.configured = True
    gateway.request_json.return_value = (
        200,
        {},
        {
            "success": True,
            "data": {"items": [], "page": None, "page_size": None, "total": 0, "total_pages": None},
            "meta": {
                "operationId": "get_product_guide",
                "pagination": {"page": None, "page_size": None, "total": 0, "total_pages": None},
            },
        },
    )
    service = CtxApiDelpiDelegationService(gateway=gateway)
    response = service.forward_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix="/90260442/guide",
        ctx_operation_id="ctx_get_product_guide",
        query={"branch": "01"},
    )
    import json

    body = json.loads(response.body.decode())
    assert body["data"]["page"] == 1
    assert body["data"]["page_size"] == 0
    assert body["data"]["total_pages"] == 0
    assert body["meta"]["pagination"]["page"] == 1
    agent = body["meta"]["agentContext"]
    assert agent["queryStatus"] == "empty"
    assert agent["emptyResult"] is True
    assert "roteiro SG2" in agent["interpretation"]
