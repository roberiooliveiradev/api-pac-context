# Importação — Agente Contexto Operacional (Custom GPT)

Pacote **somente** do que entra no builder do ChatGPT para consultar dados **Protheus/TOTVS** via API PAC Context (`ctx_*`). Documentação técnica (contrato HTTP, deploy) permanece em `docs/` na raiz.

Guia completo de configuração: [`../chatgpt-agente-contexto-operacional.md`](../chatgpt-agente-contexto-operacional.md)

Playbook de arquitetura: [`api-pac-quality/docs/playbook-api-contexto-operacional-gpt.md`](../../../api-pac-quality/docs/playbook-api-contexto-operacional-gpt.md)

---

## Checklist rápido

| Onde no builder | O que fazer | Arquivos desta pasta |
|-----------------|-------------|----------------------|
| **Descrição** | Colar texto sugerido | Ver §1 em `chatgpt-agente-contexto-operacional.md` |
| **Instruções** | Copiar/colar (≤ 8.000 caracteres) | [`instrucoes/chatgpt-instrucoes-system-prompt.txt`](instrucoes/chatgpt-instrucoes-system-prompt.txt) |
| **Conhecimento** | Upload de **todos** os arquivos da pasta | Tudo em [`conhecimento/`](conhecimento/) |
| **Actions** | Importar OpenAPI por URL (não é arquivo local) | `https://<host>/openapi.json` + Bearer `PAC_CONTEXT_API_KEY` |

**Homologação local:** `http://localhost:8011/openapi.json` (com túnel se o GPT precisar alcançar sua máquina).

**Produção (quando publicado):** ex. `https://pac-context-api.minhadelpi.com.br/openapi.json`

---

## Instruções (`instrucoes/`)

| Arquivo | Uso |
|---------|-----|
| `chatgpt-instrucoes-system-prompt.txt` | Colar integralmente no campo **Instruções** — **não** fazer upload em Conhecimento |

---

## Conhecimento (`conhecimento/`)

Fazer upload de **cada** arquivo abaixo no campo **Conhecimento** do builder:

| Arquivo | Conteúdo |
|---------|----------|
| `chatgpt-contexto-operacional-guia.md` | Mapa intenção → rota, ordem de consulta, integração com PAC, limites de chamadas |
| `chatgpt-referencia-rotas-ctx.md` | Catálogo das **28** operações `ctx_*`, parâmetros e quando usar |
| `chatgpt-distincoes-criticas.md` | O que **não** confundir (inspeção QP vs expedição, roteiro vs PCP, NC PAC vs TOTVS) |

---

## Uso junto com o Especialista Qualidade (PAC)

O **Especialista Qualidade** (api-pac-quality) grava planos, Ishikawa e 5 Porquês. Este agente **só lê** o ERP.

**Opção A — dois GPTs:** analista consulta Contexto Operacional e cola fatos na conversa do Especialista Qualidade.

**Opção B — um GPT com duas Actions:** importar OpenAPI da api-pac-quality **e** da api-pac-context (duas chaves Bearer distintas).

**Opção C — enriquecer só o PAC:** fazer upload dos **3 arquivos** de `conhecimento/` também no Especialista Qualidade (sem trocar o system prompt PAC) e adicionar a Action da api-pac-context.

---

## O que **não** importar no agente

Ficam em `docs/` (referência humana / infra):

- `chatgpt-agente-contexto-operacional.md` — manual de setup
- `contrato-http-api-pac-context-api-delpi.md` — delegação S2S
- `README.md` na raiz do repositório

---

## Após alteração neste repositório

1. Atualizar **Instruções** se mudou `instrucoes/chatgpt-instrucoes-system-prompt.txt`
2. Reenviar arquivos alterados em **Conhecimento**
3. Reimportar `/openapi.json` se a API publicou rotas novas (gate: máx. 30 operações)
