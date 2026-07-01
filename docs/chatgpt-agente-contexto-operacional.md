# ChatGPT Custom GPT — Agente Contexto Operacional

Guia para configurar o agente de **consulta ERP** (Protheus/TOTVS) no builder do ChatGPT, conectado à **api-pac-context** via Actions.

**Pré-requisitos:**

- api-pac-context em execução (local ou produção)
- Chave `PAC_CONTEXT_API_KEY` configurada no servidor
- Schema OpenAPI importado de `<base-url>/openapi.json` (**28 operações** `ctx_*`)

**Nome sugerido no builder:** `Contexto Operacional DELPI` ou `Consulta ERP Qualidade`

> **Instruções vs. Conhecimento:** o **system prompt** traz regras curtas de comportamento e limites de chamada. Mapas de rotas, distinções e catálogo ficam em **Conhecimento** — upload dos `.md`, não colar no prompt.

---

## 1. Descrição

Cole no campo **Descrição**:

```text
Assistente de leitura do Protheus/TOTVS para investigações de qualidade: produto, BOM, roteiro, OP, apontamentos, estoque, perdas, NC no ERP e inspeção de entrada. Somente consulta — não grava planos PAC. Apoia Ishikawa e 5 Porquês com fatos do chão de fábrica.
```

---

## 2. Instruções (system prompt)

O ChatGPT limita o campo **Instruções** a **8.000 caracteres**.

**Arquivo canônico:** [`agente-gpt-import/instrucoes/chatgpt-instrucoes-system-prompt.txt`](agente-gpt-import/instrucoes/chatgpt-instrucoes-system-prompt.txt)

Copie o conteúdo integralmente em **Instruções** — não faça upload desse `.txt` em Conhecimento.

---

## 3. Conhecimento (upload)

Índice: **[`agente-gpt-import/README.md`](agente-gpt-import/README.md)**

Faça upload de **todos** os arquivos em [`agente-gpt-import/conhecimento/`](agente-gpt-import/conhecimento/):

| Arquivo | Uso |
|---------|-----|
| [`chatgpt-contexto-operacional-guia.md`](agente-gpt-import/conhecimento/chatgpt-contexto-operacional-guia.md) | Mapa intenção → rota, ordem no fluxo PAC, integração |
| [`chatgpt-referencia-rotas-ctx.md`](agente-gpt-import/conhecimento/chatgpt-referencia-rotas-ctx.md) | 28 operações e parâmetros |
| [`chatgpt-distincoes-criticas.md`](agente-gpt-import/conhecimento/chatgpt-distincoes-criticas.md) | Inspeção QP vs expedição, roteiro vs PCP, NC PAC vs TOTVS |

---

## 4. Actions (OpenAPI)

| Campo | Valor |
|-------|--------|
| **Schema URL** | `https://<host-da-api>/openapi.json` |
| **Autenticação** | API Key — Header `Authorization: Bearer <PAC_CONTEXT_API_KEY>` ou `X-Api-Key` |
| **Operações** | 28 (`ctx_*`) — gate CI garante ≤ 30 |

**Local (dev):** `http://localhost:8011/openapi.json` — exige túnel (ngrok, Cloudflare Tunnel) para o ChatGPT alcançar.

**Produção (planejado):** `https://pac-context-api.minhadelpi.com.br/openapi.json`

---

## 5. Relação com Especialista Qualidade (PAC)

| Capacidade | API |
|------------|-----|
| Gravar plano, Ishikawa, 5 Porquês, ações, evidências | **api-pac-quality** (`pac_*`) |
| Casos similares, recorrência no PAC | **api-pac-quality** |
| BOM, OP, apontamento, NC TOTVS, inspeção entrada | **api-pac-context** (`ctx_*`) |

**Recomendação:** consultar contexto ERP **antes** de fechar causa raiz com alta confiança.

Para enriquecer o **mesmo** GPT do Especialista Qualidade: adicione uma segunda Action (OpenAPI context) + upload dos 3 arquivos de Conhecimento deste repositório.

---

## 6. Checklist de publicação

- [ ] `PAC_CONTEXT_API_KEY` e S2S api-delpi configurados no servidor
- [ ] Instruções: colar `agente-gpt-import/instrucoes/chatgpt-instrucoes-system-prompt.txt`
- [ ] Conhecimento: upload dos 3 arquivos em `agente-gpt-import/conhecimento/`
- [ ] Actions: importar `/openapi.json` com Bearer
- [ ] Teste: `ctx_search_products` + `ctx_get_product_structure` com produto real
- [ ] Teste: `ctx_list_nonconformities` com `item_code` + filial

---

## 7. Troubleshooting

| Sintoma | Ação |
|---------|------|
| 401 nas Actions | Conferir `PAC_CONTEXT_API_KEY` no header |
| 503 API_DELPI_MISCONFIGURED | Configurar `API_DELPI_BASE_URL` + token S2S no container |
| GPT chama rotas demais | Recolar instruções; reenviar guia §5 (máx. 3 por hipótese) |
| Confunde inspeção e expedição | Reenviar `chatgpt-distincoes-criticas.md` |
| OpenAPI rejeitado pelo ChatGPT | Rodar `scripts/audit_ctx_openapi_operation_limit.py --check` |

---

## 8. Referências

- Playbook: [`api-pac-quality/docs/playbook-api-contexto-operacional-gpt.md`](../../api-pac-quality/docs/playbook-api-contexto-operacional-gpt.md)
- Contrato HTTP: [`contrato-http-api-pac-context-api-delpi.md`](contrato-http-api-pac-context-api-delpi.md)
- Especialista Qualidade (PAC): [`api-pac-quality/docs/chatgpt-especialista-qualidade.md`](../../api-pac-quality/docs/chatgpt-especialista-qualidade.md)
