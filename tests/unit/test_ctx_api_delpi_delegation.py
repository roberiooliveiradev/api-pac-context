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


def test_delegation_consolidates_branches_when_branch_omitted():
    gateway = MagicMock()
    gateway.configured = True

    def _side_effect(method, path, query=None, json_body=None):
        branch = (query or {}).get("branch")
        if branch == "01":
            payload = {"success": True, "data": {"items": [], "total": 0}}
        else:
            payload = {
                "success": True,
                "data": {
                    "items": [{"operation_code": "01", "branch": branch or "02"}],
                    "total": 1,
                },
            }
        return 200, {}, payload

    gateway.request_json.side_effect = _side_effect
    service = CtxApiDelpiDelegationService(gateway=gateway)
    response = service.forward_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix="/90263382/guide",
        ctx_operation_id="ctx_get_product_guide",
    )
    import json

    body = json.loads(response.body.decode())
    assert body["success"] is True
    assert len(body["data"]["items"]) == 1
    agent = body["meta"]["agentContext"]
    assert agent["consolidatedAcrossBranches"] is True
    assert agent["queryStatus"] == "ok"
    assert gateway.request_json.call_count == 2


def test_delegation_fallback_when_explicit_branch_empty():
    gateway = MagicMock()
    gateway.configured = True
    calls: list[dict | None] = []

    def _side_effect(method, path, query=None, json_body=None):
        calls.append(query)
        branch = (query or {}).get("branch")
        if branch == "01":
            return 200, {}, {"success": True, "data": {"items": [], "total": 0}}
        return (
            200,
            {},
            {
                "success": True,
                "data": {"items": [{"operation_code": "01", "branch": "02"}], "total": 1},
            },
        )

    gateway.request_json.side_effect = _side_effect
    service = CtxApiDelpiDelegationService(gateway=gateway)
    response = service.forward_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix="/90263382/guide",
        ctx_operation_id="ctx_get_product_guide",
        query={"branch": "01"},
    )
    import json

    body = json.loads(response.body.decode())
    assert len(body["data"]["items"]) == 1
    agent = body["meta"]["agentContext"]
    assert agent["branchFallbackApplied"] is True
    assert agent["consolidatedAcrossBranches"] is True
    assert calls[0] == {"branch": "01"}
    assert gateway.request_json.call_count == 3


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
