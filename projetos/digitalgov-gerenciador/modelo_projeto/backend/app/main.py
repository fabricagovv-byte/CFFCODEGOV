"""API e telas do projeto {{CODIGO}}."""
from __future__ import annotations

import hmac
import os
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from . import __version__
from .db import motor, sessao
from .modelos import CicloProducao, Registro

TELAS = Path(__file__).resolve().parents[2] / "frontend"
app = FastAPI(title="{{NOME}}", version=__version__)


class RegistroNovo(BaseModel):
    titulo: str = Field(min_length=3, max_length=200)
    descricao: str | None = None


@app.get("/health")
def saude() -> dict:
    with motor().connect() as c:
        versao = c.execute(text("SELECT version_num FROM alembic_version")).scalar()
    return {"status": "ok", "projeto": "{{CODIGO}}", "versao": __version__, "migracao": versao}


@app.get("/api/registros")
def listar(s: Session = Depends(sessao)) -> list[dict]:
    return [{"id": r.id, "titulo": r.titulo, "descricao": r.descricao, "criado_em": r.criado_em.isoformat()}
            for r in s.scalars(select(Registro).order_by(Registro.id.desc()))]


@app.post("/api/registros", status_code=201)
def criar(dados: RegistroNovo, s: Session = Depends(sessao)) -> dict:
    r = Registro(**dados.model_dump())
    s.add(r)
    s.flush()
    return {"id": r.id, "titulo": r.titulo}


@app.post("/api/gerenciador/start")
def start(authorization: str | None = Header(default=None), s: Session = Depends(sessao)) -> dict:
    """Chamado pelo botão START do gerenciador central. Exige o token combinado entre os dois."""
    esperado = os.getenv("GERENCIADOR_TOKEN", "")
    recebido = (authorization or "").removeprefix("Bearer ")
    if len(esperado) < 32 or not hmac.compare_digest(recebido.encode(), esperado.encode()):
        raise HTTPException(401, "Token do gerenciador inválido")
    s.add(CicloProducao())
    s.flush()
    total = s.scalar(select(func.count()).select_from(CicloProducao))
    return {"mensagem": f"Ciclo de produção nº {total} registrado no projeto {{CODIGO}}"}


if TELAS.is_dir():
    app.mount("/static", StaticFiles(directory=TELAS), name="static")

    @app.get("/", include_in_schema=False)
    def inicio() -> FileResponse:
        return FileResponse(TELAS / "index.html")
