from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Query

from app.domain.services.ctx_delpi_operation_mapping import PRODUCTION_API_PREFIX
from app.interface.http.delegation.ctx_delpi_route_delegate import delegate_json

router = APIRouter(prefix="/production", tags=["Contexto operacional — PCP"])


def _query_params(**kwargs: Any) -> dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value is not None}


@router.get("/orders/by-op/{production_order}", operation_id="ctx_get_production_order_by_op")
def get_production_order_by_op(
    production_order: str,
    branch: str | None = Query(default=None, min_length=2, max_length=2),
    product_type: Literal["PA", "PI"] | None = Query(default=None),
    linked_sort_by: str | None = Query(default=None),
    linked_sort_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTION_API_PREFIX,
        path_suffix=f"/orders/by-op/{production_order}",
        ctx_operation_id="ctx_get_production_order_by_op",
        query=_query_params(
            branch=branch,
            product_type=product_type,
            linked_sort_by=linked_sort_by,
            linked_sort_dir=linked_sort_dir,
        ),
    )


@router.get(
    "/oee/appointments/{appointment_id}",
    operation_id="ctx_get_production_oee_appointment",
)
def get_production_oee_appointment(
    appointment_id: int,
    branch: str | None = Query(default=None),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTION_API_PREFIX,
        path_suffix=f"/oee/appointments/{appointment_id}",
        ctx_operation_id="ctx_get_production_oee_appointment",
        query=_query_params(branch=branch),
    )


@router.get("/oee", operation_id="ctx_list_production_oee")
def list_production_oee(
    branch: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    status: str | None = Query(default=None),
    efficiency_bands: str | None = Query(default=None),
    work_center: str | None = Query(default=None),
    production_order: str | None = Query(default=None),
    operator_code: str | None = Query(default=None),
    product_type: str | None = Query(default=None, pattern="^(PA|PI)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=1000),
    sort_by: str | None = Query(default=None),
    sort_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTION_API_PREFIX,
        path_suffix="/oee",
        ctx_operation_id="ctx_list_production_oee",
        query=_query_params(
            branch=branch,
            start_date=start_date,
            end_date=end_date,
            status=status,
            efficiency_bands=efficiency_bands,
            work_center=work_center,
            production_order=production_order,
            operator_code=operator_code,
            product_type=product_type,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        ),
    )


@router.get("/schedule/today", operation_id="ctx_get_production_schedule_today")
def get_production_schedule_today(
    reference_date: str | None = Query(default=None),
    branch: str | None = Query(default=None, min_length=2, max_length=2),
    limit: int | None = Query(default=None, ge=1, le=500),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTION_API_PREFIX,
        path_suffix="/schedule/today",
        ctx_operation_id="ctx_get_production_schedule_today",
        query=_query_params(reference_date=reference_date, branch=branch, limit=limit),
    )


@router.get("/orders/open", operation_id="ctx_get_production_orders_open")
def get_production_orders_open(
    reference_date: str | None = Query(default=None),
    branch: str | None = Query(default=None, min_length=2, max_length=2),
    work_center: str | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=200),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTION_API_PREFIX,
        path_suffix="/orders/open",
        ctx_operation_id="ctx_get_production_orders_open",
        query=_query_params(
            reference_date=reference_date,
            branch=branch,
            work_center=work_center,
            limit=limit,
        ),
    )


@router.get("/orders/finished", operation_id="ctx_get_production_orders_finished")
def get_production_orders_finished(
    reference_date: str | None = Query(default=None),
    branch: str | None = Query(default=None, min_length=2, max_length=2),
    work_center: str | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=200),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTION_API_PREFIX,
        path_suffix="/orders/finished",
        ctx_operation_id="ctx_get_production_orders_finished",
        query=_query_params(
            reference_date=reference_date,
            branch=branch,
            work_center=work_center,
            limit=limit,
        ),
    )


@router.get("/planned-vs-real-time", operation_id="ctx_get_production_planned_vs_real")
def get_production_planned_vs_real(
    reference_date: str | None = Query(default=None),
    branch: str | None = Query(default=None, min_length=2, max_length=2),
    work_center: str | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=200),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTION_API_PREFIX,
        path_suffix="/planned-vs-real-time",
        ctx_operation_id="ctx_get_production_planned_vs_real",
        query=_query_params(
            reference_date=reference_date,
            branch=branch,
            work_center=work_center,
            limit=limit,
        ),
    )


@router.get("/losses/records", operation_id="ctx_get_production_losses_records")
def get_production_losses_records(
    date_start: str | None = Query(default=None),
    date_end: str | None = Query(default=None),
    branch: str | None = Query(default=None, min_length=2, max_length=2),
    limit: int | None = Query(default=None, ge=1, le=200),
    loss_type: Literal["refugo", "scrap", "both"] = Query(default="both"),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTION_API_PREFIX,
        path_suffix="/losses/records",
        ctx_operation_id="ctx_get_production_losses_records",
        query=_query_params(
            date_start=date_start,
            date_end=date_end,
            branch=branch,
            limit=limit,
            loss_type=loss_type,
        ),
    )


@router.get("/losses/top-materials", operation_id="ctx_get_production_losses_top_materials")
def get_production_losses_top_materials(
    date_start: str | None = Query(default=None),
    date_end: str | None = Query(default=None),
    branch: str | None = Query(default=None, min_length=2, max_length=2),
    limit: int | None = Query(default=None, ge=1, le=200),
    loss_type: Literal["refugo", "scrap", "both"] = Query(default="both"),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTION_API_PREFIX,
        path_suffix="/losses/top-materials",
        ctx_operation_id="ctx_get_production_losses_top_materials",
        query=_query_params(
            date_start=date_start,
            date_end=date_end,
            branch=branch,
            limit=limit,
            loss_type=loss_type,
        ),
    )


@router.get(
    "/consumption/by-item/{code}",
    operation_id="ctx_get_production_consumption_by_item",
)
def get_production_consumption_by_item(
    code: str,
    date_start: str | None = Query(default=None),
    date_end: str | None = Query(default=None),
    branch: str | None = Query(default=None, min_length=2, max_length=2),
    product_group: str | None = Query(default=None, min_length=4, max_length=4),
    limit: int | None = Query(default=None, ge=1, le=200),
):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTION_API_PREFIX,
        path_suffix=f"/consumption/by-item/{code}",
        ctx_operation_id="ctx_get_production_consumption_by_item",
        query=_query_params(
            date_start=date_start,
            date_end=date_end,
            branch=branch,
            product_group=product_group,
            limit=limit,
        ),
    )
