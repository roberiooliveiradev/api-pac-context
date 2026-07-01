FROM python:3.11-slim

WORKDIR /app

COPY api-pac-context/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY api-pac-context /app

RUN chmod +x /app/docker-entrypoint.sh

ENV API_PAC_CONTEXT_PORT=8011
ENV API_PAC_ROOT_PATH=

EXPOSE 8011

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8011/health', timeout=3)" || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
