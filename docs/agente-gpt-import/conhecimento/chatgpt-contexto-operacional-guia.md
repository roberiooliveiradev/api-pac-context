# Contexto operacional DELPI — guia de investigação (Conhecimento GPT)

Upload em **Conhecimento** (`docs/agente-gpt-import/conhecimento/`), junto com `chatgpt-referencia-rotas-ctx.md` e `chatgpt-distincoes-criticas.md`. System prompt: `../instrucoes/chatgpt-instrucoes-system-prompt.txt` (colar em **Instruções**).

API: **api-pac-context** — somente **GET**, prefixo `ctx_*`, delegação à api-delpi.

---

## 1. Quando usar este agente

| Situação | Use contexto operacional | Use Especialista Qualidade (PAC) |
|----------|--------------------------|----------------------------------|
| «Qual a BOM do 90123456?» | Sim | Não |
| «Qual OP produziu o lote?» | Sim | Não |
| «Já houve NC parecida no TOTVS?» | Sim (`ctx_list_nonconformities`) | Casos similares **no PAC** é outra API |
| «Registrar Ishikawa / gravar plano» | Não | Sim |
| «Causa raiz e confiança %» | Só fatos que embasam | Sim (fecha análise) |

---

## 2. Pré-requisitos antes de chamar a API

| Dado | Obrigatório? | Como obter |
|------|--------------|------------|
| Código do produto | Quase sempre | Relato, NF, etiqueta ou `ctx_search_products` |
| Filial `01` ou `02` | Muitas rotas | Perguntar ao analista — **não** inferir só por CEP |
| Número da OP | Rotas de OP/apontamento | Relato, etiqueta, `ctx_get_product_production_status` |
| Período (datas) | NC, perdas, movimentos | Padrão sugerido: 12 meses até a data do relato |

### Código de produto exato (8 dígitos)

Quando o analista informar **só o código** (ex.: `90260882`, `10080022`):

1. **Preferir** `ctx_get_product_detail` — `GET /products/{code}` (cadastro direto).
2. **Alternativa:** `ctx_search_products` com query `code=90260882` (não usar path `/products/search/{code}` — **não existe**).
3. **Não** usar busca ampla sem filtro para «confirmar» um código já informado.

A API responde em ambos os caminhos; o detalhe por path é mais estável no Custom GPT Actions.

---

## 3. Mapa intenção → rota primária

Use **uma** rota primária por pergunta. Detalhes e parâmetros: `chatgpt-referencia-rotas-ctx.md`.

| Pergunta do analista (exemplo) | Rota `ctx_*` | Ishikawa / 5 Porquês |
|--------------------------------|--------------|----------------------|
| «Qual o código / cadastro do item?» | `ctx_search_products` → `ctx_get_product_detail` | Identificação |
| «Resumo rápido do produto» | `ctx_get_product_summary` | Contexto |
| «Qual a estrutura / componentes?» | `ctx_get_product_structure` | **Material** |
| «MP exclusiva ou alternativas?» | `ctx_get_product_structure_exclusivity` | Material |
| «Qual o roteiro de fabricação?» | `ctx_get_product_guide` | **Método**, **Máquina** |
| «Quais ensaios QP no cadastro?» | `ctx_get_product_inspection` | **Medição** |
| «OPs e apontamentos do PA até a data?» | `ctx_get_product_production_status` | Máquina, Mão de obra, Método |
| «Visão integrada fábrica» | `ctx_get_product_factory_status` | Panorama |
| «Quantidade após inspeção final / expedição» | `ctx_get_product_shipping_status` | Medição, expedição |
| «Saldo em estoque na filial?» | `ctx_get_product_stock` | Material |
| «Movimentos internos / rastreio OP» | `ctx_get_product_internal_movements` | Material, rastreabilidade |
| «Onde este item é usado (BOM reversa)?» | `ctx_get_product_parents` | Material |
| «Desenho técnico existe?» | `ctx_get_product_drawing` | Engenharia |
| «Detalhe da OP citada no relato» | `ctx_get_production_order_by_op` | OP, vínculos |
| «Detalhe de um apontamento (id)» | `ctx_get_production_oee_appointment` | Tempos, achados |
| «Listar apontamentos (filtros)» | `ctx_list_production_oee` | Máquina, operador |
| «O que está programado hoje no PCP?» | `ctx_get_production_schedule_today` | PCP |
| «OPs abertas / finalizadas» | `ctx_get_production_orders_open` / `ctx_get_production_orders_finished` | PCP |
| «Planejado × real (desvio tempo)» | `ctx_get_production_planned_vs_real` | Método, Máquina |
| «Registros de refugo / scrap» | `ctx_get_production_losses_records` | Material, perdas |
| «MPs com mais perdas no período» | `ctx_get_production_losses_top_materials` | Material |
| «Consumo real da MP no PA» | `ctx_get_production_consumption_by_item` | Material |
| «NC já registradas no Protheus?» | `ctx_list_nonconformities` | Gestão, histórico |
| «Histórico inspeção recebimento MP» | `ctx_get_inspecoes_entrada_historico` | Material, fornecedor |
| «Laudo / ensaios QER da entrada» | `ctx_get_inspecoes_entrada_detalhe` | Material, Medição |
| «Quantidade produzida (inspeção final)» | `ctx_get_produced_quantity` | Medição, volume |

---

## 4. Ordem sugerida no fluxo PAC

Após o analista confirmar **filial** e **produto** (e OP/lote se houver):

1. `ctx_search_products` ou `ctx_get_product_detail`
2. `ctx_get_product_production_status` **ou** `ctx_get_production_order_by_op` (se OP conhecida)
3. `ctx_get_product_structure` + `ctx_get_product_guide`
4. `ctx_list_nonconformities` (mesmo `item_code`, janela de datas)
5. **Durante** 5 Porquês — conforme hipótese:
   - Material / fornecedor → `ctx_get_inspecoes_entrada_detalhe`, `ctx_get_production_consumption_by_item`
   - Máquina / método → `ctx_get_production_oee_appointment`, `ctx_get_production_planned_vs_real`
   - Perda / refugo → `ctx_get_production_losses_records`
   - Estoque → `ctx_get_product_stock`, `ctx_get_product_internal_movements`

**Não** executar os 5 passos automaticamente em toda conversa — adapte à pergunta.

---

## 5. Regras de chamada

1. **Leitura antes de suposição** — consulte ERP antes de o analista fechar causa com confiança alta.
2. **Uma intenção → uma rota primária** — tabela §3.
3. **Máximo 3 APIs por hipótese** — se insuficiente, liste lacunas e peça confirmação (outra OP, outro período, outro código).
4. **Não duplicar o PAC** — `similar-cases`, recorrência e gravação ficam na api-pac-quality.
5. **Resposta ao analista** — resumo em PT-BR; anexar IDs técnicos (OP, id apontamento) só quando úteis para próxima pergunta.

---

## 6. Integração com Especialista Qualidade

| Passo | Quem |
|-------|------|
| Extrair relato, filial, escopo NC | Especialista Qualidade |
| Consultar BOM, OP, NC TOTVS, laudo entrada | **Contexto operacional** (este agente) |
| Ishikawa, 5 Porquês, causa + **% confiança** | Especialista Qualidade |
| Gravar plano, ações, evidências | Especialista Qualidade |

Se o analista usar **um único GPT** com duas Actions: rotule na resposta se o fato veio do **ERP** ou do **histórico PAC**.

---

## 7. Erros frequentes

| Erro | Correção |
|------|----------|
| Analista mandou código exato e GPT falhou | Usar `ctx_get_product_detail` (`/products/{code}`), não só `search` |
| Confundir inspeção QP com expedição | Ver `chatgpt-distincoes-criticas.md` |
| Chamar `ctx_get_product_guide` esperando PCP do dia | Use `ctx_get_production_schedule_today` |
| Listar NC TOTVS achando que é plano PAC | São cadastros diferentes |
| Buscar sem filial em rotas de inspeção entrada | `branch` obrigatório `01` ou `02` |
| Expor `ctx_*` ou JSON cru ao analista | Resumir em linguagem de chão de fábrica |

---

## 8. Evolução (composites — fase P3)

Quando disponíveis na API, preferir endpoints compostos (uma chamada GPT):

| Composto | Agrupa |
|----------|--------|
| `ctx_investigate_product` | detail + structure + guide + production-status |
| `ctx_investigate_production_order` | by-op + oee list + planned-vs-real |
| `ctx_investigate_incoming_quality` | historico + detalhe + rejeitadas |

Até lá, orquestrar manualmente com o limite de 3 chamadas por hipótese.
