# Contrato HTTP api-pac-context ↔ api-delpi

Delegação **server-to-server** de leitura investigativa. A **api-pac-context** expõe `ctx_*` no OpenAPI; a **api-delpi** permanece fonte de verdade.

## Princípio

- **Sem persistência local** — apenas repasse de path/query
- **Sem CRUD PAC** — permanece em api-pac-quality
- **Somente GET** (fases P1–P2)

## Configuração

```env
API_DELPI_BASE_URL=http://delpi-api-delpi:8000
API_DELPI_INTERNAL_SERVICE_TOKEN=<token>
PAC_CONTEXT_API_KEY=<chave GPT>
```

## Mapeamento allowlist §8 (28 operações)

### Produto (P1 + extensão)

| ctx_* | api-delpi operationId | Path |
|-------|----------------------|------|
| `ctx_search_products` | `search_products` | `GET /products/search` |
| `ctx_get_product_detail` | `get_product_detail` | `GET /products/{code}` |
| `ctx_get_product_summary` | `get_product_summary` | `GET /products/{code}/summary` |
| `ctx_get_product_structure` | `get_product_structure` | `GET /products/{code}/structure` |
| `ctx_get_product_structure_exclusivity` | `get_product_structure_exclusivity` | `GET /products/{code}/structure/exclusivity` |
| `ctx_get_product_guide` | `get_product_guide` | `GET /products/{code}/guide` |
| `ctx_get_product_inspection` | `get_product_inspection` | `GET /products/{code}/inspection` |
| `ctx_get_product_production_status` | `get_product_production_status` | `GET /products/{code}/production-status` |
| `ctx_get_product_factory_status` | `get_product_factory_status` | `GET /products/{code}/factory-status` |
| `ctx_get_product_shipping_status` | `get_product_shipping_status` | `GET /products/{code}/shipping-status` |
| `ctx_get_product_stock` | `get_product_stock` | `GET /products/{code}/stock` |
| `ctx_get_product_internal_movements` | `get_product_internal_movements` | `GET /products/{code}/internal-movements` |
| `ctx_get_product_parents` | `get_product_parents` | `GET /products/{code}/parents` |
| `ctx_get_product_drawing` | `get_product_drawing` | `GET /products/{code}/drawing` |

### PCP / produção (P2)

| ctx_* | api-delpi operationId | Path |
|-------|----------------------|------|
| `ctx_get_production_order_by_op` | `get_production_order_by_op` | `GET /production/orders/by-op/{production_order}` |
| `ctx_get_production_oee_appointment` | `get_production_oee_appointment_by_id` | `GET /production/oee/appointments/{appointment_id}` |
| `ctx_list_production_oee` | `get_production_oee` | `GET /production/oee` |
| `ctx_get_production_schedule_today` | `get_production_schedule_today` | `GET /production/schedule/today` |
| `ctx_get_production_orders_open` | `get_production_orders_open` | `GET /production/orders/open` |
| `ctx_get_production_orders_finished` | `get_production_orders_finished` | `GET /production/orders/finished` |
| `ctx_get_production_planned_vs_real` | `get_production_planned_vs_real_time` | `GET /production/planned-vs-real-time` |
| `ctx_get_production_losses_records` | `get_production_losses_records` | `GET /production/losses/records` |
| `ctx_get_production_losses_top_materials` | `get_production_losses_top_materials` | `GET /production/losses/top-materials` |
| `ctx_get_production_consumption_by_item` | `get_production_consumption_by_item` | `GET /production/consumption/by-item/{code}` |

### Qualidade TOTVS (P2)

| ctx_* | api-delpi operationId | Path |
|-------|----------------------|------|
| `ctx_list_nonconformities` | `list_nonconformities` | `GET /quality/nonconformities` |
| `ctx_get_inspecoes_entrada_historico` | `get_inspecoes_entrada_historico` | `GET /inspecoes-entrada/historico` |
| `ctx_get_inspecoes_entrada_detalhe` | `get_inspecoes_entrada_historico_detalhe` | `GET /inspecoes-entrada/historico/detalhe` |
| `ctx_get_produced_quantity` | `get_produced_quantity` | `GET /quality/produced-quantity` |

A resposta repassa o envelope api-delpi; `meta.operationId` é reescrito para `ctx_*`.

## Erros

| HTTP | code | Quando |
|------|------|--------|
| 401 | `UNAUTHORIZED` | Sem `PAC_CONTEXT_API_KEY` válida |
| 503 | `API_DELPI_MISCONFIGURED` | Env S2S ausente |
| 503 | `API_DELPI_UNAVAILABLE` | api-delpi inacessível |

Referência irmã: `api-pac-quality/docs/contrato-http-api-pac-api-delpi.md`.
