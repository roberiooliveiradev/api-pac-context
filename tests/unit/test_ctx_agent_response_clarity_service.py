from __future__ import annotations

from app.domain.services.ctx_agent_response_clarity_service import CtxAgentResponseClarityService


def test_paged_list_empty_adds_agent_context_and_normalizes_pagination():
    payload = {
        "success": True,
        "data": {"items": [], "page": None, "page_size": None, "total": 0, "total_pages": None},
        "meta": {"pagination": {"page": None, "page_size": None, "total": 0, "total_pages": None}},
    }

    result = CtxAgentResponseClarityService.enrich_success_payload(
        payload,
        "ctx_get_product_guide",
    )

    assert result["data"]["page"] == 1
    assert result["data"]["page_size"] == 0
    agent = result["meta"]["agentContext"]
    assert agent["queryStatus"] == "empty"
    assert agent["emptyResult"] is True
    assert agent["hasData"] is False
    assert "roteiro SG2" in agent["interpretation"]
    assert result["meta"]["pagination"]["page"] == 1


def test_playbook_report_counts_items():
    payload = {
        "success": True,
        "data": {"items": [{"op": "001"}, {"op": "002"}], "summary": {"total": 2}},
    }

    result = CtxAgentResponseClarityService.enrich_success_payload(
        payload,
        "ctx_get_production_orders_open",
    )
    agent = result["meta"]["agentContext"]
    assert agent["queryStatus"] == "ok"
    assert agent["recordCount"] == 2
    assert agent["shape"] == "playbook_report"


def test_composite_analysis_detects_factory_status():
    payload = {
        "success": True,
        "data": {
            "factory_status": "OP ABERTA / NÃO INICIADO",
            "structure": {"items": []},
            "production": {"items": [{"production_order": "001"}]},
        },
    }

    result = CtxAgentResponseClarityService.enrich_success_payload(
        payload,
        "ctx_get_product_factory_status",
    )
    agent = result["meta"]["agentContext"]
    assert agent["queryStatus"] == "ok"
    assert agent["hasData"] is True
    assert agent["shape"] == "composite_analysis"


def test_scalar_drawing_not_found():
    payload = {
        "success": True,
        "data": {"found": False, "product_code": "90260442", "message": "Desenho PDF não encontrado"},
    }

    result = CtxAgentResponseClarityService.enrich_success_payload(
        payload,
        "ctx_get_product_drawing",
    )
    agent = result["meta"]["agentContext"]
    assert agent["queryStatus"] == "not_found"
    assert "biblioteca" in agent["interpretation"].lower()


def test_product_snapshot_ok():
    payload = {
        "success": True,
        "data": {"product": {"product_code": "90260882", "description": "CHICOTE"}},
    }

    result = CtxAgentResponseClarityService.enrich_success_payload(
        payload,
        "ctx_get_product_detail",
    )
    agent = result["meta"]["agentContext"]
    assert agent["queryStatus"] == "ok"
    assert agent["recordCount"] == 1
    assert agent["shape"] == "product_snapshot"


def test_guide_empty_with_branch_suggests_alternate_filial():
    payload = {
        "success": True,
        "data": {"items": [], "total": 0, "page": None, "page_size": None},
    }

    result = CtxAgentResponseClarityService.enrich_success_payload(
        payload,
        "ctx_get_product_guide",
        request_query={"branch": "01"},
    )

    agent = result["meta"]["agentContext"]
    assert agent["queryStatus"] == "empty"
    assert agent["requestFilters"] == {"branch": "01"}
    assert "filial 01" in agent["interpretation"]
    assert "02" in agent["interpretation"]


def test_error_agent_context():
    agent = CtxAgentResponseClarityService.build_error_agent_context(
        error_code="API_DELPI_UNAVAILABLE",
        recoverable=True,
        interpretation_key="error.gateway",
    )
    assert agent["queryStatus"] == "error"
    assert agent["apiSuccess"] is False
    assert "api-delpi" in agent["interpretation"]
