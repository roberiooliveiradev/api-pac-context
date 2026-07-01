from __future__ import annotations

from app.domain.services import ctx_operational_branch_policy as branch_policy
from app.domain.services.ctx_multi_branch_response_merge_service import (
    CtxMultiBranchResponseMergeService,
)


def test_should_consolidate_when_branch_omitted_on_guide():
    assert branch_policy.should_consolidate_branches(
        "ctx_get_product_guide",
        {"page": 1},
    )


def test_should_not_consolidate_when_branch_informed():
    assert not branch_policy.should_consolidate_branches(
        "ctx_get_product_guide",
        {"branch": "01"},
    )


def test_should_not_consolidate_inspecoes_entrada():
    assert not branch_policy.should_consolidate_branches(
        "ctx_get_inspecoes_entrada_historico",
        None,
    )


def test_merge_paged_list_payloads_from_two_branches():
    merged = CtxMultiBranchResponseMergeService.merge(
        [
            {
                "success": True,
                "data": {"items": [{"operation_code": "01", "branch": "01"}], "total": 1},
            },
            {
                "success": True,
                "data": {"items": [{"operation_code": "02", "branch": "02"}], "total": 1},
            },
        ],
        "ctx_get_product_guide",
    )

    assert merged["success"] is True
    assert len(merged["data"]["items"]) == 2
    assert merged["data"]["total"] == 2


def test_should_retry_without_branch_when_explicit_branch_empty():
    assert branch_policy.should_retry_without_branch(
        "ctx_get_product_guide",
        {"branch": "01"},
        empty_result=True,
        api_success=True,
    )
