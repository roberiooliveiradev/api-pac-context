from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.domain.services.ctx_delpi_operation_mapping import QUALITY_API_PREFIX
from app.interface.http.delegation.ctx_delpi_route_delegate import delegate_json

router = APIRouter(prefix="/quality", tags=["Contexto operacional — qualidade TOTVS"])


def _query_params(**kwargs: Any) -> dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value is not None}


@router.get("/nonconformities", operation_id="ctx_list_nonconformities")
def list_nonconformities(
    type: str = Query(default="all", pattern="^(internal|external|all)$"),
    branch: str | None = Query(default=None),
    date_start: str | None = Query(default=None),
    date_end: str | None = Query(default=None),
    status: str | None = Query(default=None),
    item_code: str | None = Query(default=None),
    description: str | None = Query(default=None),
    page: int | None = Query(default=None, ge=1),
    page_size: int | None = Query(default=None, ge=1),
):
    return delegate_json(
        method="GET",
        path_prefix=QUALITY_API_PREFIX,
        path_suffix="/nonconformities",
        ctx_operation_id="ctx_list_nonconformities",
        query=_query_params(
            type=type,
            branch=branch,
            date_start=date_start,
            date_end=date_end,
            status=status,
            item_code=item_code,
            description=description,
            page=page,
            page_size=page_size,
        ),
    )


@router.get("/produced-quantity", operation_id="ctx_get_produced_quantity")
def get_produced_quantity(
    product: list[str] = Query(
        ...,
        description="Código(s) do produto; repetível ou separado por vírgula",
    ),
    branch: str | None = Query(default=None),
    date_start: str | None = Query(default=None),
    date_end: str | None = Query(default=None),
):
    return delegate_json(
        method="GET",
        path_prefix=QUALITY_API_PREFIX,
        path_suffix="/produced-quantity",
        ctx_operation_id="ctx_get_produced_quantity",
        query=_query_params(
            product=product,
            branch=branch,
            date_start=date_start,
            date_end=date_end,
        ),
    )
