# Referência — rotas `ctx_*` (Conhecimento GPT)

Catálogo das **28** operações publicadas na api-pac-context (allowlist playbook §8). Mapa de intenção: `chatgpt-contexto-operacional-guia.md`.

Todas as rotas são **GET**. Resposta: envelope api-delpi (`success`, `data`, `meta`); `meta.operationId` vem como `ctx_*`.

---

## Produto (`/products`)

| ctx_* | Quando usar | Parâmetros principais |
|-------|-------------|------------------------|
| `ctx_search_products` | Resolver código por descrição, grupo, ref. cliente | `code`, `description`, `group_code`, `customer_reference`, `page`, `page_size` |
| `ctx_get_product_detail` | **Código exato já informado** (8 dígitos) — preferir em vez de search | `code` (path), `view` (`full` \| `summary`), `legacy` |
| `ctx_get_product_summary` | Contexto rápido (cadastro + amostra estoque) | `code` |
| `ctx_get_product_structure` | BOM / componentes | `code`, `max_depth`, `page`, `page_size` |
| `ctx_get_product_structure_exclusivity` | MP exclusiva / alternativas | `code`, `max_depth`, `legacy` |
| `ctx_get_product_guide` | Roteiro (CTs, operações) | `code`, `branch`, `page`, `page_size`, `max_depth` |
| `ctx_get_product_inspection` | Ensaios **QP** no cadastro do produto | `code`, `page`, `page_size`, `max_depth` |
| `ctx_get_product_production_status` | OPs e apontamentos do PA até data ref. | `code`, `reference_date`, `max_depth`, `branch`, `legacy` |
| `ctx_get_product_factory_status` | Visão integrada (estrutura + OP + expedição) | `code`, `reference_date`, `date_start`, `date_end`, `branch`, `legacy` |
| `ctx_get_product_shipping_status` | PA após inspeção **final** | `code`, `reference_date`, `date_start`, `date_end`, `branch`, `legacy` |
| `ctx_get_product_stock` | Saldo por filial / armazém | `code`, `branch`, `warehouse`, `location`, `page`, `page_size`, `legacy` |
| `ctx_get_product_internal_movements` | Movimentos internos (filtro OP) | `code`, `date_start`, `date_end`, `branch`, `location`, `tm`, `op`, `page`, `page_size` |
| `ctx_get_product_parents` | BOM reversa — onde o item é usado | `code`, `max_depth`, `page`, `page_size` |
| `ctx_get_product_drawing` | Metadados do desenho PDF | `code` |

---

## Produção / PCP (`/production`)

| ctx_* | Quando usar | Parâmetros principais |
|-------|-------------|------------------------|
| `ctx_get_production_order_by_op` | Detalhe da OP do relato | `production_order`, `branch`, `product_type` (`PA` \| `PI`), `linked_sort_by`, `linked_sort_dir` |
| `ctx_get_production_oee_appointment` | Detalhe de **um** apontamento (id numérico) | `appointment_id`, `branch` |
| `ctx_list_production_oee` | Listar apontamentos com filtros | `branch`, `start_date`, `end_date`, `status`, `work_center`, `production_order`, `operator_code`, `product_type`, `page`, `page_size`, `sort_by`, `sort_dir` |
| `ctx_get_production_schedule_today` | Programação PCP do dia | `reference_date`, `branch`, `limit` |
| `ctx_get_production_orders_open` | OPs em aberto | `reference_date`, `branch`, `work_center`, `limit` |
| `ctx_get_production_orders_finished` | OPs finalizadas na janela | `reference_date`, `branch`, `work_center`, `limit` |
| `ctx_get_production_planned_vs_real` | Desvio tempo planejado × real | `reference_date`, `branch`, `work_center`, `limit` |
| `ctx_get_production_losses_records` | Registros de refugo/scrap | `date_start`, `date_end`, `branch`, `limit`, `loss_type` (`refugo` \| `scrap` \| `both`) |
| `ctx_get_production_losses_top_materials` | Ranking MPs com mais perdas | `date_start`, `date_end`, `branch`, `limit`, `loss_type` |
| `ctx_get_production_consumption_by_item` | Consumo real da MP em PAs | `code` (MP), `date_start`, `date_end`, `branch`, `product_group`, `limit` |

---

## Qualidade TOTVS (`/quality`, `/inspecoes-entrada`)

| ctx_* | Quando usar | Parâmetros principais |
|-------|-------------|------------------------|
| `ctx_list_nonconformities` | NC cadastradas no **Protheus** | `type` (`internal` \| `external` \| `all`), `branch`, `date_start`, `date_end`, `status`, `item_code`, `description`, `page`, `page_size` |
| `ctx_get_produced_quantity` | Quantidade produzida (CT inspeção final) | `product` (lista, obrigatório), `branch`, `date_start`, `date_end` |
| `ctx_get_inspecoes_entrada_historico` | Histórico recebimento MP | `branch` (**obrig.** `01` \| `02`), `page`, `page_size`, `result`, `date_from`, `date_to`, `supplier`, `product_code`, `inspector`, `invoice_number`, `lot` |
| `ctx_get_inspecoes_entrada_detalhe` | Laudo + ensaios QER | `branch` (**obrig.**), `inspection_id` (**obrig.**) |

---

## Dicas de combinação (sem exceder 3 chamadas)

| Cenário | Sequência sugerida |
|---------|-------------------|
| «Investigar produto reclamado» | detail → production-status → structure |
| «OP 123456 está correta?» | by-op → (se id apontamento) oee_appointment |
| «MP X falhou na entrada?» | historico (product_code) → detalhe (inspection_id) |
| «Há padrão de NC no item?» | list_nonconformities (`item_code` + 12 meses) |

---

## Fora desta API (não chamar)

| Necessidade | Onde |
|-------------|------|
| Criar/atualizar plano PAC, Ishikawa, ações | api-pac-quality (`pac_*`) |
| Casos similares no histórico PAC | `pac_search_similar_cases` |
| SQL ad hoc | Não exposto ao GPT contexto |
| KPIs agregados de dashboard | Fora da allowlist `ctx_*` |

Contrato técnico completo: `docs/contrato-http-api-pac-context-api-delpi.md` (não upload no GPT).
