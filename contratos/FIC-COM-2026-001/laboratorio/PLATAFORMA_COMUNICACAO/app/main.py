"""Plataforma de Comunicação Institucional: aplicação web (API + telas)."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import acesso
from .comum import now  # noqa: F401  (usado pela linha de comando)
from .db import init
from .rotas import auditoria, campanhas, canais, chamados, contatos, painel, publicacoes, usuarios

PASTA_TELAS = Path(__file__).resolve().parents[1] / "static"

CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; "
    "frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
)
SEM_CSP = ("/docs", "/redoc", "/openapi.json")  # a documentação interativa carrega recursos externos


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI):
    init()
    yield


app = FastAPI(title="Comunicação Institucional", version="1.1.0", lifespan=ciclo_de_vida)
app.mount("/static", StaticFiles(directory=str(PASTA_TELAS)), name="static")
for modulo in (acesso, usuarios, painel, canais, publicacoes, campanhas, contatos, chamados, auditoria):
    app.include_router(modulo.router)


@app.middleware("http")
async def cabecalhos_de_seguranca(request: Request, call_next):
    resposta = await call_next(request)
    caminho = request.url.path
    if not caminho.startswith(SEM_CSP):
        resposta.headers["Content-Security-Policy"] = CSP
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    resposta.headers["X-Frame-Options"] = "DENY"
    resposta.headers["Referrer-Policy"] = "no-referrer"
    if caminho.startswith("/api") or caminho == "/health":
        resposta.headers["Cache-Control"] = "no-store"
    return resposta


@app.get("/", include_in_schema=False)
def pagina_inicial() -> FileResponse:
    return FileResponse(PASTA_TELAS / "index.html")


@app.get("/health")
def saude() -> dict:
    return {"status": "ok", "system": "comunicacao", "production_ready": False}
