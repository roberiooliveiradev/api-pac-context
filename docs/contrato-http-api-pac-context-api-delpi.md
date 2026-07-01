# Contrato HTTP api-pac-context ↔ api-delpi

Delegação **server-to-server** de leitura investigativa. A **api-pac-context** expõe `ctx_*` no OpenAPI; a **api-delpi** permanece fonte de verdade.

## Princípio

- **Sem persistência local** — apenas repasse de path/query
- **Sem CRUD PAC** — permanece em api-pac-quality
- **Somente GET** na fase P1 (produto)

## Configuração

```env
API_DELPI_BASE_URL=http://delpi-api-delpi:8000
API_DELPI_INTERNAL_SERVICE_TOKEN=<token>
PAC_CONTEXT_API_KEY=<chave GPT>
```

## Mapeamento P1 (produto)

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

A resposta repassa o envelope api-delpi; `meta.operationId` é reescrito para `ctx_*`.

## Erros

| HTTP | code | Quando |
|------|------|--------|
| 401 | `UNAUTHORIZED` | Sem `PAC_CONTEXT_API_KEY` válida |
| 503 | `API_DELPI_MISCONFIGURED` | Env S2S ausente |
| 503 | `API_DELPI_UNAVAILABLE` | api-delpi inacessível |

Referência irmã: `api-pac-quality/docs/contrato-http-api-pac-api-delpi.md`.
