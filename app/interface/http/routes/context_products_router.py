from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.domain.services.ctx_delpi_operation_mapping import PRODUCTS_API_PREFIX
from app.interface.http.delegation.ctx_delpi_route_delegate import delegate_json

router = APIRouter(prefix="/products", tags=["Contexto operacional — produto"])


def _query_params(**kwargs: Any) -> dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value is not None}


@router.get("/search", operation_id="ctx_search_products")
def search_products(
    code: str | None = Query(default=None),
    group_code: str | None = Query(default=None),
    description: str | None = Query(default=None),
    customer_reference: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    sort: str | None = Query(default=None),
    direction: str | None = Query(default=None),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix="/search",
        ctx_operation_id="ctx_search_products",
        query=_query_params(
            code=code,
            group_code=group_code,
            description=description,
            customer_reference=customer_reference,
            page=page,
            page_size=page_size,
            sort=sort,
            direction=direction,
        ),
    )


@router.get("/{code}", operation_id="ctx_get_product_detail")
def get_product_detail(
    code: str,
    view: str = Query(default="full", description="full ou summary"),
    legacy: bool = Query(default=False),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}",
        ctx_operation_id="ctx_get_product_detail",
        query=_query_params(view=view, legacy=legacy),
    )


@router.get("/{code}/summary", operation_id="ctx_get_product_summary")
def get_product_summary(code: str):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}/summary",
        ctx_operation_id="ctx_get_product_summary",
    )


@router.get("/{code}/structure", operation_id="ctx_get_product_structure")
def get_product_structure(
    code: str,
    max_depth: int | None = Query(default=None, ge=1, le=100),
    page: int | None = Query(default=None, ge=1),
    page_size: int | None = Query(default=None, ge=1, le=500),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}/structure",
        ctx_operation_id="ctx_get_product_structure",
        query=_query_params(max_depth=max_depth, page=page, page_size=page_size),
    )


@router.get(
    "/{code}/structure/exclusivity",
    operation_id="ctx_get_product_structure_exclusivity",
)
def get_product_structure_exclusivity(
    code: str,
    max_depth: int | None = Query(default=None, ge=1, le=100),
    legacy: bool = Query(default=False),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}/structure/exclusivity",
        ctx_operation_id="ctx_get_product_structure_exclusivity",
        query=_query_params(max_depth=max_depth, legacy=legacy),
    )


@router.get("/{code}/guide", operation_id="ctx_get_product_guide")
def get_product_guide(
    code: str,
    branch: str | None = Query(default=None, min_length=2, max_length=2),
    page: int | None = Query(default=None, ge=1),
    page_size: int | None = Query(default=None, ge=1, le=500),
    max_depth: int | None = Query(default=None, ge=1, le=15),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}/guide",
        ctx_operation_id="ctx_get_product_guide",
        query=_query_params(branch=branch, page=page, page_size=page_size, max_depth=max_depth),
    )


@router.get("/{code}/inspection", operation_id="ctx_get_product_inspection")
def get_product_inspection(
    code: str,
    page: int | None = Query(default=None, ge=1),
    page_size: int | None = Query(default=None, ge=1, le=500),
    max_depth: int | None = Query(default=None, ge=1, le=15),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}/inspection",
        ctx_operation_id="ctx_get_product_inspection",
        query=_query_params(page=page, page_size=page_size, max_depth=max_depth),
    )


@router.get("/{code}/production-status", operation_id="ctx_get_product_production_status")
def get_product_production_status(
    code: str,
    reference_date: str | None = Query(default=None),
    max_depth: int | None = Query(default=None, ge=1, le=100),
    branch: str | None = Query(default=None, min_length=2, max_length=2),
    legacy: bool = Query(default=False),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}/production-status",
        ctx_operation_id="ctx_get_product_production_status",
        query=_query_params(
            reference_date=reference_date,
            max_depth=max_depth,
            branch=branch,
            legacy=legacy,
        ),
    )


@router.get("/{code}/factory-status", operation_id="ctx_get_product_factory_status")
def get_product_factory_status(
    code: str,
    reference_date: str | None = Query(default=None),
    date_start: str | None = Query(default=None),
    date_end: str | None = Query(default=None),
    max_depth: int | None = Query(default=None, ge=1, le=100),
    branch: str | None = Query(default=None, min_length=2, max_length=2),
    legacy: bool = Query(default=False),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}/factory-status",
        ctx_operation_id="ctx_get_product_factory_status",
        query=_query_params(
            reference_date=reference_date,
            date_start=date_start,
            date_end=date_end,
            max_depth=max_depth,
            branch=branch,
            legacy=legacy,
        ),
    )


@router.get("/{code}/shipping-status", operation_id="ctx_get_product_shipping_status")
def get_product_shipping_status(
    code: str,
    reference_date: str | None = Query(default=None),
    date_start: str | None = Query(default=None),
    date_end: str | None = Query(default=None),
    branch: str | None = Query(default=None, min_length=2, max_length=2),
    legacy: bool = Query(default=False),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}/shipping-status",
        ctx_operation_id="ctx_get_product_shipping_status",
        query=_query_params(
            reference_date=reference_date,
            date_start=date_start,
            date_end=date_end,
            branch=branch,
            legacy=legacy,
        ),
    )


@router.get("/{code}/stock", operation_id="ctx_get_product_stock")
def get_product_stock(
    code: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    branch: str | None = Query(default=None),
    warehouse: str | None = Query(default=None),
    location: str | None = Query(default=None),
    legacy: bool = Query(default=False),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}/stock",
        ctx_operation_id="ctx_get_product_stock",
        query=_query_params(
            page=page,
            page_size=page_size,
            branch=branch,
            warehouse=warehouse,
            location=location,
            legacy=legacy,
        ),
    )


@router.get("/{code}/internal-movements", operation_id="ctx_get_product_internal_movements")
def get_product_internal_movements(
    code: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    date_start: str | None = Query(default=None),
    date_end: str | None = Query(default=None),
    branch: str | None = Query(default=None),
    location: str | None = Query(default=None),
    tm: str | None = Query(default=None),
    op: str | None = Query(default=None),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}/internal-movements",
        ctx_operation_id="ctx_get_product_internal_movements",
        query=_query_params(
            page=page,
            page_size=page_size,
            date_start=date_start,
            date_end=date_end,
            branch=branch,
            location=location,
            tm=tm,
            op=op,
        ),
    )


@router.get("/{code}/parents", operation_id="ctx_get_product_parents")
def get_product_parents(
    code: str,
    max_depth: int | None = Query(default=None),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}/parents",
        ctx_operation_id="ctx_get_product_parents",
        query=_query_params(max_depth=max_depth, page=page, page_size=page_size),
    )


@router.get("/{code}/drawing", operation_id="ctx_get_product_drawing")
def get_product_drawing(code: str):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}/drawing",
        ctx_operation_id="ctx_get_product_drawing",
    )
