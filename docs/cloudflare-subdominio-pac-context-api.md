# Subdomínio Cloudflare — `pac-context-api.minhadelpi.com.br`

Guia para expor a **API PAC Context** na internet (agente GPT investigador ERP).

**URL pública:** `https://pac-context-api.minhadelpi.com.br`

---

## Visão geral

```
Internet
   │
   ▼
Cloudflare (TLS + proxy)
   │
   ▼
cloudflared (srv-api) ──► localhost:8083 ──► api-pac-context-nginx ──► api-pac-context:8011
```

No **srv-api**:

| Porta | Serviço |
|-------|---------|
| `80` | `delpi-gateway` |
| `8082` | `api-pac-quality-nginx` |
| `8083` | `api-pac-context-nginx` (esta API) |

O container `cloudflared` já existe — adicione um **Public Hostname** ao tunnel existente.

---

## Pré-requisitos

1. Stack no ar:

   ```bash
   cd ~/projetos/api-pac-context
   cp .env.srv-api.example .env
   # PAC_CONTEXT_API_KEY + API_DELPI_INTERNAL_SERVICE_TOKEN do infra
   cp docker-compose.override.srv-api.example.yml docker-compose.override.yml
   docker compose up -d --build
   ```

2. Health local:

   ```bash
   curl -s http://localhost:8083/health
   ```

   Esperado: `"api_delpi_delegation":"configured"`, `"published_operations":28`.

3. Porta livre:

   ```bash
   ss -tlnp | grep ':8083 '
   ```

---

## Passo 1 — Public Hostname no tunnel

### Dashboard (recomendado)

1. [Cloudflare Zero Trust](https://one.dash.cloudflare.com/) → **Networks** → **Tunnels**
2. Abra o tunnel do srv-api (mesmo de `minhadelpi.com.br`)
3. **Public Hostname** → **Add a public hostname**

| Campo | Valor |
|-------|--------|
| **Subdomain** | `pac-context-api` |
| **Domain** | `minhadelpi.com.br` |
| **Path** | *(vazio)* |
| **Type** | `HTTP` |
| **URL** | `localhost:8083` |

4. Salvar

### Arquivo `config.yml` (alternativa)

```yaml
ingress:
  # ... hostnames existentes ...
  - hostname: pac-api.minhadelpi.com.br
    service: http://localhost:8082
  - hostname: pac-context-api.minhadelpi.com.br
    service: http://localhost:8083
  - service: http_status:404
```

```bash
docker restart cloudflared
```

---

## Passo 2 — Validar

```bash
# srv-api
curl -s http://localhost:8083/health

# Internet (após propagar DNS)
curl -s https://pac-context-api.minhadelpi.com.br/health
curl -s -o /dev/null -w "%{http_code}\n" https://pac-context-api.minhadelpi.com.br/docs
```

Teste autenticado:

```bash
curl -s -H "Authorization: Bearer $PAC_CONTEXT_API_KEY" \
  "https://pac-context-api.minhadelpi.com.br/products/search?code=90&page_size=1"
```

---

## Passo 3 — `.env` no srv-api

```env
PUBLIC_BASE_URL=https://pac-context-api.minhadelpi.com.br
NGINX_HTTP_PORT=8083
PAC_CONTEXT_API_KEY=<openssl rand -hex 32>
API_DELPI_BASE_URL=http://delpi-api-delpi:8000
API_DELPI_INTERNAL_SERVICE_TOKEN=<delpi-central/infra/.env>
```

Se mudar `NGINX_HTTP_PORT`, atualize o tunnel (`localhost:PORT`).

---

## Passo 4 — Custom GPT

1. **Actions** → importar `https://pac-context-api.minhadelpi.com.br/openapi.json`
2. Autenticação: **API Key** / Bearer com `PAC_CONTEXT_API_KEY`
3. **Conhecimento:** upload de `docs/agente-gpt-import/conhecimento/` (3 arquivos)
4. **Instruções:** `docs/agente-gpt-import/instrucoes/chatgpt-instrucoes-system-prompt.txt`

Detalhes: [chatgpt-acoes-api-key.md](chatgpt-acoes-api-key.md) · [chatgpt-agente-contexto-operacional.md](chatgpt-agente-contexto-operacional.md)

---

## Troubleshooting

| Sintoma | Ação |
|---------|------|
| `522` / timeout | Conferir hostname → `localhost:8083`; `docker compose ps` |
| `502` | `docker compose logs api-pac-context` |
| `401` | `PAC_CONTEXT_API_KEY` no `.env` e no GPT |
| `api_delpi_delegation: misconfigured` | Token S2S + rede `infra_delpi-network` |
| Health OK local, HTTPS falha | Aguardar DNS; conferir tunnel |

---

## Checklist

- [ ] `.env` com `PAC_CONTEXT_API_KEY` e `API_DELPI_INTERNAL_SERVICE_TOKEN`
- [ ] `docker-compose.override.yml` na rede `infra_delpi-network`
- [ ] `curl http://localhost:8083/health` → OK
- [ ] Public Hostname `pac-context-api.minhadelpi.com.br` → `http://localhost:8083`
- [ ] `curl https://pac-context-api.minhadelpi.com.br/health` → OK
- [ ] OpenAPI importado no GPT (28 ops)

Ver também: [DEPLOYMENT.md](DEPLOYMENT.md)
