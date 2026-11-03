"""MOD-006 — Consulta à trilha de auditoria (somente leitura)."""
from __future__ import annotations

from datetime import date, datetime, time, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import exigir
from ..models import RegistroAuditoria, Usuario
from ..schemas import PaginaAuditoria

router = APIRouter(prefix="/api/auditoria", tags=["auditoria"])


@router.get("", response_model=PaginaAuditoria)
def listar(acao: str | None = None, usuario_id: int | None = None, recurso: str | None = None,
           de: date | None = None, ate: date | None = None,
           pagina: int = Query(1, ge=1), por_pagina: int = Query(50, ge=1, le=200),
           db: Session = Depends(get_db), _: Usuario = Depends(exigir("auditoria:ler"))):
    q = select(RegistroAuditoria)
    if acao:
        q = q.where(RegistroAuditoria.acao == acao)
    if usuario_id:
        q = q.where(RegistroAuditoria.usuario_id == usuario_id)
    if recurso:
        q = q.where(RegistroAuditoria.recurso == recurso)
    if de:
        q = q.where(RegistroAuditoria.momento >= datetime.combine(de, time.min, timezone.utc))
    if ate:
        q = q.where(RegistroAuditoria.momento <= datetime.combine(ate, time.max, timezone.utc))
    total = db.scalar(select(func.count()).select_from(q.subquery()))
    itens = db.scalars(q.order_by(RegistroAuditoria.id.desc()).offset((pagina - 1) * por_pagina).limit(por_pagina)).all()
    return {"total": total, "pagina": pagina, "por_pagina": por_pagina, "itens": itens}


@router.get("/acoes")
def acoes(db: Session = Depends(get_db), _: Usuario = Depends(exigir("auditoria:ler"))):
    return sorted(db.scalars(select(RegistroAuditoria.acao).distinct()).all())
