# Plataforma de Comunicação Institucional — API e telas (FastAPI)
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 DG_COMM_DB=/dados/comunicacao.db
WORKDIR /app
RUN groupadd --system app && useradd --system --gid app --home /app app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app
COPY migrations ./migrations
COPY static ./static
RUN mkdir -p /dados && chown app:app /dados
USER app
EXPOSE 8765
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8765/health').status == 200 else 1)"
# Aplica as migrações pendentes e sobe a API. A porta 8765 fica só na rede interna; o acesso externo passa pelo Nginx.
CMD ["sh", "-c", "python -m app.cli init && uvicorn app.main:app --host 0.0.0.0 --port 8765 --proxy-headers --forwarded-allow-ips=${FORWARDED_ALLOW_IPS:-*} --workers ${WORKERS:-2}"]
