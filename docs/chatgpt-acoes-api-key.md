# ChatGPT Custom GPT — Actions API PAC Context

Conectar o GPT de **contexto operacional** via chave `PAC_CONTEXT_API_KEY`.

**URL:** `https://pac-context-api.minhadelpi.com.br`

---

## 1. Chave no servidor

```bash
openssl rand -hex 32
```

Em `~/projetos/api-pac-context/.env`:

```env
PAC_CONTEXT_API_KEY=cole_o_token_aqui
```

```bash
cd ~/projetos/api-pac-context
docker compose up -d --force-recreate api-pac-context
```

Teste:

```bash
curl -s -H "Authorization: Bearer SEU_TOKEN" \
  "https://pac-context-api.minhadelpi.com.br/products/search?page_size=1"
```

Sem token → `401`. Com token → `200`.

---

## 2. OpenAPI no GPT

1. **Importar de URL:** `https://pac-context-api.minhadelpi.com.br/openapi.json`
2. Servidor: `https://pac-context-api.minhadelpi.com.br`
3. **28 operações** `ctx_*` (limite ChatGPT: 30)
4. Autenticação: **API Key** — Header `Authorization` — `Bearer <PAC_CONTEXT_API_KEY>`

Alternativa equivalente: header `X-Api-Key`.

---

## 3. Dois GPTs vs um GPT com duas Actions

| Modelo | Actions |
|--------|---------|
| Especialista Qualidade | `pac-api.minhadelpi.com.br` + `PAC_QUALITY_API_KEY` |
| Contexto Operacional | `pac-context-api.minhadelpi.com.br` + `PAC_CONTEXT_API_KEY` |

É possível um único GPT com **duas** importações OpenAPI e duas chaves (uma por servidor).

---

## 4. Homologação local (tunnel rápido)

```bash
cloudflared tunnel --url http://localhost:8083
```

Use a URL `*.trycloudflare.com` no builder — expira ao encerrar o processo.

Subdomínio permanente: [cloudflare-subdominio-pac-context-api.md](cloudflare-subdominio-pac-context-api.md)
