# Distinções críticas — produto, PCP e qualidade (Conhecimento GPT)

Evitar confusões que geram **causa raiz errada** na investigação PAC. Complementa `chatgpt-contexto-operacional-guia.md`.

---

## 1. Inspeção no produto vs expedição

| Conceito | Rota | O que representa |
|----------|------|------------------|
| Ensaios **QP** cadastrados no produto | `ctx_get_product_inspection` | Plano de inspeção / características no cadastro — **não** é resultado de lote específico |
| Quantidade após inspeção **final** do PA | `ctx_get_product_shipping_status` | Pós-produção, liberado para expedição |
| Laudo de **recebimento** de MP | `ctx_get_inspecoes_entrada_*` | Entrada de matéria-prima do fornecedor |
| Quantidade **produzida** (volume para PPM) | `ctx_get_produced_quantity` | Agregado por produto/período — não substitui rastreio por OP |

**Erro típico:** usar `inspection` achando que mostra falha do lote reclamado → na verdade é o **cadastro** de ensaios. Para lote/OP, começar por `production-status` ou `by-op`.

---

## 2. Roteiro vs programação PCP

| Conceito | Rota | O que representa |
|----------|------|------------------|
| **Roteiro** de fabricação (CT, operações SG2) | `ctx_get_product_guide` | Como o produto **deve** ser feito (engenharia de processo) |
| **Programação** do dia | `ctx_get_production_schedule_today` | O que o PCP **planejou** para hoje |
| OPs abertas / finalizadas | `ctx_get_production_orders_open` / `finished` | Status operacional em janela |
| Apontamento realizado | `ctx_list_production_oee` / `ctx_get_production_oee_appointment` | O que **foi** executado na máquina |

**Erro típico:** perguntar «qual máquina rodou o lote?» só com `guide` → o roteiro diz o CT **previsto**; confirme com apontamento ou `production-status`.

---

## 3. Estrutura vs exclusividade vs pais

| Rota | Uso |
|------|-----|
| `ctx_get_product_structure` | BOM **para baixo** — componentes do PA/PI |
| `ctx_get_product_structure_exclusivity` | MPs exclusivas / alternativas na estrutura |
| `ctx_get_product_parents` | BOM **para cima** — em quais PAs esta MP aparece |

---

## 4. NC PAC vs NC TOTVS

| Fonte | API | Significado |
|-------|-----|-------------|
| **Plano de ação PAC** (Minha DELPI) | api-pac-quality | Investigação estruturada, Ishikawa, 5 Porquês, ações |
| **NC no Protheus** | `ctx_list_nonconformities` | Registros legados/sistêmicos no ERP |

Ambos podem coexistir para o mesmo produto — **não** assumir que listar TOTVS substitui `pac_search_similar_cases`.

---

## 5. Estoque vs movimento vs consumo

| Rota | Pergunta que responde |
|------|----------------------|
| `ctx_get_product_stock` | «Quanto tem em estoque agora?» |
| `ctx_get_product_internal_movements` | «Quais movimentos internos (incl. OP)?» |
| `ctx_get_production_consumption_by_item` | «Quanto desta MP foi consumida na produção de PAs?» |
| `ctx_get_production_losses_records` | «Onde houve refugo/scrap registrado?» |

---

## 6. Factory-status — quando usar

`ctx_get_product_factory_status` agrega visão **integrada** (estrutura + OP + expedição). Útil para panorama inicial; para hipótese específica (ex.: só refugo), prefira a rota **especializada** da tabela de intenções.

---

## 7. Filial

- Muitas rotas aceitam `branch` opcional (`01` / `02`).
- **Inspeções de entrada:** `branch` **obrigatório** — sem filial a API retorna erro de validação.
- Não inferir filial pelo cliente ou CEP; confirmar com o analista.

---

## 8. PA vs PI

Em rotas de produção, `product_type` pode ser `PA` (produto acabado) ou `PI` (intermediário). Se o relato não deixar claro, pergunte ou consulte `ctx_get_product_detail` antes de filtrar.

---

## 9. Desenho técnico

`ctx_get_product_drawing` retorna **metadados** do PDF (não o binário). Para análise dimensional detalhada, o analista pode abrir o desenho no processo habitual da empresa; o agente cita revisão/caminho se vier no retorno.

---

## 11. Lista vazia ≠ erro de API

Rotas `paged_list` (ex.: `ctx_get_product_guide`, `ctx_search_products`, `ctx_list_nonconformities`) podem retornar:

```json
{ "success": true, "data": { "items": [], "total": 0, "page": 1, "page_size": 0 } }
```

| Interpretação | Correto | Incorreto |
|---------------|---------|-----------|
| `items: []`, `total: 0` | Sem roteiro / sem NC / sem match no filtro | «Erro de comunicação com a API» |
| `success: false` ou HTTP 5xx | Falha técnica real | Tratar como dado ausente |

Para **roteiro vazio** do PA: informar ao analista que o ERP não tem operações SG2 cadastradas para aquele código/filial — sugerir estrutura (BOM) ou status de produção.

---

Ao explicar distinções, use exemplos de chão de fábrica:

- ❌ «O `ctx_get_product_inspection` não tem dados do lote»
- ✅ «O cadastro de ensaios do produto não mostra o resultado da inspeção **deste** lote — vamos buscar pela OP ou pelo recebimento da MP»
