#!/usr/bin/env bash
# Pós-deploy srv-api — health local + HTTPS opcional.
set -euo pipefail

CTX_API_URL="${CTX_API_URL:-https://pac-context-api.minhadelpi.com.br}"
LOCAL_HEALTH_URL="${LOCAL_HEALTH_URL:-http://localhost:8083/health}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "== API PAC Context pós-deploy =="
echo "Público: ${CTX_API_URL}"
echo "Local:   ${LOCAL_HEALTH_URL}"
echo ""

echo "[check] Health local (nginx)"
if curl -sf "${LOCAL_HEALTH_URL}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d.get('service') == 'api-pac-context', d
assert d.get('api_delpi_delegation') == 'configured', d
ops = int(d.get('published_operations', 0))
assert ops >= 28, f'published_operations={ops}'
print('  OK', d)
"; then
  :
else
  echo "  FALHA — suba a stack: cd ${REPO_ROOT} && docker compose up -d --build" >&2
  exit 1
fi

echo ""
echo "[check] OpenAPI gate (repo)"
if [ -x "${REPO_ROOT}/.venv/bin/python" ]; then
  "${REPO_ROOT}/.venv/bin/python" "${REPO_ROOT}/scripts/audit_ctx_openapi_operation_limit.py" --check
elif command -v python3 >/dev/null 2>&1; then
  python3 "${REPO_ROOT}/scripts/audit_ctx_openapi_operation_limit.py" --check
else
  echo "  [skip] python não disponível para gate OpenAPI"
fi

echo ""
echo "[check] Health HTTPS (opcional)"
if curl -sf "${CTX_API_URL}/health" >/dev/null 2>&1; then
  echo "  OK ${CTX_API_URL}/health"
else
  echo "  [warn] HTTPS ainda indisponível — configure cloudflared (docs/cloudflare-subdominio-pac-context-api.md)"
fi

echo ""
echo "Próximos passos:"
echo "  1. Cloudflare: pac-context-api.minhadelpi.com.br → localhost:8083"
echo "  2. GPT: importar ${CTX_API_URL}/openapi.json + PAC_CONTEXT_API_KEY"
echo "  3. Conhecimento: docs/agente-gpt-import/conhecimento/ (3 arquivos)"
echo ""
echo "[OK] post_deploy_verify"
