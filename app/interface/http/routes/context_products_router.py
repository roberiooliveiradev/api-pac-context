from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.domain.services.ctx_delpi_operation_mapping import PRODUCTS_API_PREFIX
from app.interface.http.delegation.ctx_delpi_route_delegate import delegate_json

router = APIRouter(prefix="/products", tags=["Contexto operacional — produto"])


def _query_params(**kwargs: Any) -> dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value is not None}


@router.get(
    "/search",
    operation_id="ctx_search_products",
    summary="Buscar produtos (filtros opcionais)",
    description=(
        "Listagem paginada com filtros. Para **código exato** já informado pelo analista "
        "(ex. 90260882), prefira `ctx_get_product_detail` em `/products/{code}`. "
        "Parâmetro `code` = query string, não path."
    ),
)
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


@router.get(
    "/{code}",
    operation_id="ctx_get_product_detail",
    summary="Cadastro do produto por código exato",
    description=(
        "Use quando o analista informar o **código completo** do item (8 dígitos). "
        "Retorna cadastro `full` ou `summary`."
    ),
)
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


@router.get(
    "/{code}/summary",
    operation_id="ctx_get_product_summary",
    summary="Resumo cadastral do produto",
    description="Visão resumida do cadastro. Para código exato completo, prefira `ctx_get_product_detail`.",
)
def get_product_summary(code: str):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}/summary",
        ctx_operation_id="ctx_get_product_summary",
    )


@router.get(
    "/{code}/structure",
    operation_id="ctx_get_product_structure",
    summary="Estrutura BOM (para baixo)",
    description=(
        "Componentes do produto (PA/PI/MP). `items` vazio com `success: true` = sem BOM vigente — "
        "não é erro de API. Ver `meta.agentContext.interpretation`."
    ),
)
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
    summary="Exclusividade de MPs na estrutura",
    description="MPs exclusivas e alternativas na BOM. Lista vazia = sem componentes exclusivos cadastrados.",
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


@router.get(
    "/{code}/guide",
    operation_id="ctx_get_product_guide",
    summary="Roteiro de fabricação (SG2)",
    description=(
        "Operações e centros de trabalho do produto. `items` vazio com `success: true` "
        "significa **sem roteiro cadastrado** no ERP — não é erro de API. Informe `branch` 01 ou 02."
    ),
)
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


@router.get(
    "/{code}/inspection",
    operation_id="ctx_get_product_inspection",
    summary="Plano de inspeção cadastrado (QP)",
    description=(
        "Ensaios **cadastrados** no produto — não é resultado de lote/OP específica. "
        "`items` vazio = sem plano no ERP. Ver `meta.agentContext`."
    ),
)
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


@router.get(
    "/{code}/production-status",
    operation_id="ctx_get_product_production_status",
    summary="Status de produção do produto",
    description="OPs e apontamentos por nível da estrutura. Informe `reference_date` e `branch` quando possível.",
)
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


@router.get(
    "/{code}/factory-status",
    operation_id="ctx_get_product_factory_status",
    summary="Panorama integrado de fábrica",
    description=(
        "Análise composta (estrutura + OP + expedição). `meta.agentContext.hasData=true` "
        "mesmo com seções vazias se houver `factory_status`."
    ),
)
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


@router.get(
    "/{code}/shipping-status",
    operation_id="ctx_get_product_shipping_status",
    summary="Status pós-inspeção final / expedição",
    description="Quantidades liberadas após inspeção final do PA — distinto do plano QP em `/inspection`.",
)
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


@router.get(
    "/{code}/stock",
    operation_id="ctx_get_product_stock",
    summary="Saldo de estoque do produto",
    description="Posição atual por filial/armazém. Lista vazia = sem saldo nos filtros — não é erro de API.",
)
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


@router.get(
    "/{code}/internal-movements",
    operation_id="ctx_get_product_internal_movements",
    summary="Movimentos internos do produto",
    description="Histórico de movimentações internas (incl. OP). Filtre por período e filial.",
)
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


@router.get(
    "/{code}/parents",
    operation_id="ctx_get_product_parents",
    summary="Onde o item é usado (BOM para cima)",
    description="PA/PI que consomem este código como componente. Vazio = item não aparece como MP/PI em outras estruturas.",
)
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


@router.get(
    "/{code}/drawing",
    operation_id="ctx_get_product_drawing",
    summary="Metadados do desenho PDF",
    description=(
        "Metadados apenas (não baixa o PDF). `data.found=false` = desenho ausente na biblioteca — "
        "veja `meta.agentContext.queryStatus=not_found`."
    ),
)
def get_product_drawing(code: str):
    return delegate_json(
        method="GET",
        path_prefix=PRODUCTS_API_PREFIX,
        path_suffix=f"/{code}/drawing",
        ctx_operation_id="ctx_get_product_drawing",
    )
