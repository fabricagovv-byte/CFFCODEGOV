"""Aplicação FastAPI — Atendimento ao Cidadão."""
from __future__ import annotations

import logging
import re
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .config import config
from .db import engine
from .modulos import routers as routers_modulos
from .routers import arquivos, auditoria, auth, documentos, painel, pesquisa, usuarios

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("gd.http")

app = FastAPI(title="Gestão Documental Pública", version="0.1.0",
              description="Atendimento ao Cidadão — API do sistema.",
              docs_url=None if config.env == "prod" else "/api/docs",
              openapi_url=None if config.env == "prod" else "/api/openapi.json", redoc_url=None)

_RID = re.compile(r"^[A-Za-z0-9-]{1,64}$")

app.add_middleware(CORSMiddleware, allow_origins=config.cors_origins, allow_credentials=False,
                   allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["Authorization", "Content-Type"])


@app.middleware("http")
async def seguranca_e_log(request: Request, call_next):
    rid = request.headers.get("x-request-id", "")
    if not _RID.match(rid):
        rid = uuid.uuid4().hex
    ini = time.perf_counter()
    resp = await call_next(request)
    resp.headers["X-Request-ID"] = rid
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if not request.url.path.startswith("/api/docs"):
        resp.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    resp.headers["Cache-Control"] = "no-store"
    log.info("rid=%s %s %s -> %s %.1fms", rid, request.method, request.url.path, resp.status_code,
             (time.perf_counter() - ini) * 1000)
    return resp


for r in (auth, usuarios, documentos, arquivos, pesquisa, painel, auditoria):
    app.include_router(r.router)
for r in routers_modulos():  # módulos gerados (app/modulos/*)
    app.include_router(r)


@app.get("/api/health", tags=["saúde"])
def health():
    return {"status": "ok", "ambiente": config.env, "versao": app.version}


@app.get("/api/health/db", tags=["saúde"])
def health_db():
    with engine.connect() as c:
        c.execute(text("SELECT 1"))
    return {"status": "ok", "banco": engine.dialect.name}
