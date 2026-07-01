# API PAC Context — contexto operacional para GPT

BFF de **somente leitura** que delega à **api-delpi** com autenticação S2S. Consumidor primário: Custom GPT investigador (`ctx_*`, máx. 30 operações OpenAPI).

Espelha o padrão da [api-pac-quality](../api-pac-quality). Playbook: [playbook-api-contexto-operacional-gpt.md](../api-pac-quality/docs/playbook-api-contexto-operacional-gpt.md).

## Fase atual (P2)

- Health, auth (`PAC_CONTEXT_API_KEY`), gateway S2S
- **28 rotas** allowlist §8 playbook (produto + PCP + qualidade TOTVS)
- Gate CI: `scripts/audit_ctx_openapi_operation_limit.py --check`

## Execução local

```bash
cd api-pac-context
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# editar PAC_CONTEXT_API_KEY, API_DELPI_BASE_URL, API_DELPI_INTERNAL_SERVICE_TOKEN

uvicorn app.asgi:application --reload --port 8011
```

## Testes

```bash
chmod +x scripts/ci-smoke.sh
./scripts/ci-smoke.sh
```

## Variáveis

| Variável | Descrição |
|----------|-----------|
| `PAC_CONTEXT_API_KEY` | Chave do Custom GPT (Bearer / X-Api-Key) |
| `API_DELPI_BASE_URL` | Base da api-delpi |
| `API_DELPI_INTERNAL_SERVICE_TOKEN` | Token S2S (mesmo do delpi-central) |
| `PUBLIC_BASE_URL` | URL pública no OpenAPI |

## Headers S2S (saída → api-delpi)

- `X-Delpi-Service-Token` / `Authorization: Bearer`
- `X-Delpi-Caller-App: api-pac-context`
- `X-Delpi-Actor-Id: ctx-gpt-agent`

## Roadmap

| Fase | Entrega |
|------|---------|
| P1 | 10 rotas produto |
| P2 | +18 rotas PCP/qualidade (allowlist §8 — **28 ops**) |
| P3 | Composites (`ctx_investigate_product`, …) |
