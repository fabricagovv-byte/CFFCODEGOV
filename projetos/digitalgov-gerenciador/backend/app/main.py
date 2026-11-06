"""Gerenciador Central DigitalGov: API e painel."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from . import __version__, acesso
from .rotas import cadastros, documentos, horas, painel, projetos, relatorios, usuarios

PASTA_TELAS = Path(__file__).resolve().parents[2] / "frontend"
CSP = ("default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; "
       "frame-ancestors 'none'; base-uri 'none'; form-action 'self'")

app = FastAPI(title="Gerenciador Central DigitalGov", version=__version__)
for modulo in (acesso, usuarios, painel, projetos, horas, documentos, relatorios, cadastros):
    app.include_router(modulo.router)


@app.exception_handler(IntegrityError)
def erro_integridade(_: Request, erro: IntegrityError) -> JSONResponse:
    motivo = str(getattr(erro, "orig", erro)).split("\n")[0]
    if "foreign key" in motivo.lower() or "violates foreign key" in motivo.lower():
        texto = "O registro relacionado não existe ou ainda está em uso"
    elif "unique" in motivo.lower() or "duplicate" in motivo.lower():
        texto = "Já existe um registro com este valor"
    else:
        texto = "Dados não aceitos pelo banco"
    return JSONResponse({"detail": texto}, status_code=409)


@app.exception_handler(ValidationError)
def erro_validacao(_: Request, erro: ValidationError) -> JSONResponse:
    return JSONResponse({"detail": [{"msg": e["msg"], "loc": e["loc"]} for e in erro.errors()]}, status_code=422)


@app.middleware("http")
async def cabecalhos(request: Request, call_next):
    resposta = await call_next(request)
    if not request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
        resposta.headers["Content-Security-Policy"] = CSP
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    resposta.headers["X-Frame-Options"] = "DENY"
    resposta.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path.startswith("/api"):
        resposta.headers["Cache-Control"] = "no-store"
    return resposta


@app.get("/api/health")
def saude() -> dict:
    return {"status": "ok", "sistema": "gerenciador", "versao": __version__}


if PASTA_TELAS.is_dir():
    app.mount("/static", StaticFiles(directory=PASTA_TELAS), name="static")

    @app.get("/", include_in_schema=False)
    def inicio() -> FileResponse:
        return FileResponse(PASTA_TELAS / "index.html")
