from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.domain.services.ctx_delpi_operation_mapping import INSPECOES_ENTRADA_API_PREFIX
from app.interface.http.delegation.ctx_delpi_route_delegate import delegate_json

router = APIRouter(
    prefix="/inspecoes-entrada",
    tags=["Contexto operacional — inspeções de entrada"],
)


def _query_params(**kwargs: Any) -> dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value is not None}


@router.get("/historico", operation_id="ctx_get_inspecoes_entrada_historico")
def get_inspecoes_entrada_historico(
    branch: str = Query(..., min_length=2, max_length=2, pattern="^(01|02)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    result: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    supplier: str | None = Query(default=None),
    product_code: str | None = Query(default=None),
    inspector: str | None = Query(default=None),
    invoice_number: str | None = Query(default=None),
    lot: str | None = Query(default=None),
):
    return delegate_json(
        method="GET",
        path_prefix=INSPECOES_ENTRADA_API_PREFIX,
        path_suffix="/historico",
        ctx_operation_id="ctx_get_inspecoes_entrada_historico",
        query=_query_params(
            branch=branch,
            page=page,
            page_size=page_size,
            result=result,
            date_from=date_from,
            date_to=date_to,
            supplier=supplier,
            product_code=product_code,
            inspector=inspector,
            invoice_number=invoice_number,
            lot=lot,
        ),
    )


@router.get("/historico/detalhe", operation_id="ctx_get_inspecoes_entrada_detalhe")
def get_inspecoes_entrada_detalhe(
    branch: str = Query(..., min_length=2, max_length=2, pattern="^(01|02)$"),
    inspection_id: str = Query(..., min_length=1),
):
    return delegate_json(
        method="GET",
        path_prefix=INSPECOES_ENTRADA_API_PREFIX,
        path_suffix="/historico/detalhe",
        ctx_operation_id="ctx_get_inspecoes_entrada_detalhe",
        query=_query_params(branch=branch, inspection_id=inspection_id),
    )
