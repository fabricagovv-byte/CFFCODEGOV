# Gerenciador Central DigitalGov (API + painel)
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 GERENCIADOR_ARQUIVOS=/dados/arquivos
RUN apt-get update && apt-get install -y --no-install-recommends git postgresql-client && rm -rf /var/lib/apt/lists/*
WORKDIR /srv/gerenciador
RUN groupadd --system app && useradd --system --gid app --home /srv/gerenciador app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install -r backend/requirements.txt
COPY backend backend
COPY frontend frontend
COPY modelo_projeto modelo_projeto
COPY infra infra
RUN mkdir -p /dados/arquivos && chown -R app:app /dados
USER app
WORKDIR /srv/gerenciador/backend
EXPOSE 8200
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8200/api/health').status==200 else 1)"
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8200 --proxy-headers"]
