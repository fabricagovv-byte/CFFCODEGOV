"""MOD-004 — Pesquisa documental por texto e filtros."""
from __future__ import annotations

from datetime import date, datetime, time, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..deps import exigir
from ..models import Arquivo, Documento, Usuario
from ..permissions import VISIBILIDADE
from ..schemas import PaginaDocumentos

router = APIRouter(prefix="/api/pesquisa", tags=["pesquisa"])


def _escapar(t: str) -> str:
    return t.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@router.get("", response_model=PaginaDocumentos)
def pesquisar(q: str = Query("", max_length=200), tipo: str | None = None, status: str | None = None,
              classificacao: str | None = None, de: date | None = None, ate: date | None = None,
              pagina: int = Query(1, ge=1), por_pagina: int = Query(20, ge=1, le=100),
              db: Session = Depends(get_db), u: Usuario = Depends(exigir("doc:ler"))):
    visiveis = VISIBILIDADE[u.perfil]
    consulta = select(Documento).where(Documento.classificacao.in_(visiveis))
    for termo in q.split():
        padrao = f"%{_escapar(termo.lower())}%"
        em_arquivo = select(Arquivo.documento_id).where(func.lower(Arquivo.nome_original).like(padrao, escape="\\"))
        consulta = consulta.where(or_(
            func.lower(Documento.numero).like(padrao, escape="\\"),
            func.lower(Documento.titulo).like(padrao, escape="\\"),
            func.lower(Documento.assunto).like(padrao, escape="\\"),
            func.lower(Documento.interessado).like(padrao, escape="\\"),
            func.lower(Documento.tipo).like(padrao, escape="\\"),
            Documento.id.in_(em_arquivo)))
    if tipo:
        consulta = consulta.where(Documento.tipo == tipo)
    if status:
        consulta = consulta.where(Documento.status == status)
    if classificacao:
        consulta = consulta.where(Documento.classificacao == classificacao)
    if de:
        consulta = consulta.where(Documento.criado_em >= datetime.combine(de, time.min, timezone.utc))
    if ate:
        consulta = consulta.where(Documento.criado_em <= datetime.combine(ate, time.max, timezone.utc))
    total = db.scalar(select(func.count()).select_from(consulta.subquery()))
    itens = db.scalars(consulta.options(selectinload(Documento.arquivos))
                       .order_by(Documento.criado_em.desc(), Documento.id.desc())
                       .offset((pagina - 1) * por_pagina).limit(por_pagina)).all()
    return {"total": total, "pagina": pagina, "por_pagina": por_pagina, "itens": itens}


@router.get("/tipos")
def tipos(db: Session = Depends(get_db), u: Usuario = Depends(exigir("doc:ler"))):
    return sorted(db.scalars(select(Documento.tipo).where(Documento.classificacao.in_(VISIBILIDADE[u.perfil]))
                             .distinct()).all())
