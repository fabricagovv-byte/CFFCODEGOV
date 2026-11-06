# Painel de controle da fábrica (uso interno da contratada; não expor à internet)
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 DG_FACTORY_DB=/dados/factory.db
WORKDIR /app
RUN groupadd --system app && useradd --system --gid app --home /app app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app
COPY config ./config
COPY static ./static
RUN mkdir -p /dados && chown app:app /dados
USER app
EXPOSE 8777
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8777/health').status == 200 else 1)"
CMD ["sh", "-c", "python -m app.cli init && uvicorn app.main:app --host 0.0.0.0 --port 8777"]
