# Backend — FastAPI (MOD-007)
FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN groupadd --system app && useradd --system --gid app --home /app app
COPY requirements.txt .
# CA_EXTRA (opcional): certificado de proxy corporativo com inspeção TLS; não fica na imagem.
RUN --mount=type=secret,id=ca_extra,required=false \
    if [ -s /run/secrets/ca_extra ]; then export PIP_CERT=/run/secrets/ca_extra; fi; \
    pip install -r requirements.txt
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini .
RUN mkdir -p /dados/uploads && chown -R app:app /dados
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health').status==200 else 1)"
# Aplica migrações e sobe a API. A porta 8000 só é exposta na rede interna (o Nginx sobrescreve X-Forwarded-For).
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips=${FORWARDED_ALLOW_IPS:-*} --workers ${WORKERS:-2}"]
