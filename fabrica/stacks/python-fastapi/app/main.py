"""{{NOME}} — API (esqueleto da fábrica)."""
from fastapi import FastAPI

app = FastAPI(title="{{NOME}}", docs_url="/api/docs", openapi_url="/api/openapi.json")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "sistema": "{{NOME}}"}
