# Deploy — API PAC Context

Stack **autônoma**: API FastAPI + **nginx próprio**. Não passa pelo gateway `delpi-central`. Somente leitura investigativa (`ctx_*`) com delegação S2S à api-delpi.

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| [contrato-http-api-pac-context-api-delpi.md](contrato-http-api-pac-context-api-delpi.md) | Delegação leitura → api-delpi |
| [chatgpt-acoes-api-key.md](chatgpt-acoes-api-key.md) | Custom GPT — chave `PAC_CONTEXT_API_KEY` |
| [chatgpt-agente-contexto-operacional.md](chatgpt-agente-contexto-operacional.md) | Setup do agente contexto |
| [agente-gpt-import/README.md](agente-gpt-import/README.md) | Arquivos Conhecimento GPT |
| [cloudflare-subdominio-pac-context-api.md](cloudflare-subdominio-pac-context-api.md) | Tunnel Cloudflare |
| `GET /openapi.json` | **28 operações** `ctx_*` |

## Estrutura

```
api-pac-context/
  Dockerfile              # API (uvicorn :8011)
  docker-compose.yml      # api-pac-context + nginx
  nginx/
    Dockerfile
    nginx.conf            # pac-context-api → api:8011
```

| Serviço | Container | Porta no host |
|---------|-----------|---------------|
| API | `api-pac-context` | interna `8011` |
| Nginx | `api-pac-context-nginx` | `NGINX_HTTP_PORT` (ex.: `8083`) |

## Subir no srv-api

```bash
cd ~/projetos/api-pac-context
git pull
cp .env.srv-api.example .env
grep '^API_DELPI_INTERNAL_SERVICE_TOKEN=' ~/projetos/delpi-central/infra/.env
# colar token + PAC_CONTEXT_API_KEY (openssl rand -hex 32)
nano .env
cp docker-compose.override.srv-api.example.yml docker-compose.override.yml

docker compose up -d --build
curl -s http://localhost:8083/health
```

Resposta esperada:

```json
{
  "status": "ok",
  "service": "api-pac-context",
  "api_delpi_delegation": "configured",
  "published_operations": 28,
  "phase": "P2"
}
```

## Portas no srv-api

| Porta host | Uso |
|------------|-----|
| `80` | `delpi-gateway` |
| `8082` | nginx **api-pac-quality** |
| `8083` | nginx **api-pac-context** (`NGINX_HTTP_PORT`) |

## Cloudflare

**URL pública:** `https://pac-context-api.minhadelpi.com.br`

Guia: **[cloudflare-subdominio-pac-context-api.md](cloudflare-subdominio-pac-context-api.md)**

## Atualizar após `git pull`

```bash
cd ~/projetos/api-pac-context
git pull
docker compose up -d --build
bash scripts/post_deploy_verify.sh
```

## Testes locais (container)

```bash
chmod +x scripts/ci-smoke.sh scripts/post_deploy_verify.sh
./scripts/ci-smoke.sh
```
