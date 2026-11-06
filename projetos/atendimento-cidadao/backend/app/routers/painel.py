"""MOD-005 — Painel administrativo (indicadores)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import exigir
from ..models import Arquivo, Documento, RegistroAuditoria, Usuario
from ..schemas import AuditoriaOut

router = APIRouter(prefix="/api/painel", tags=["painel"])


def _contagem(db: Session, coluna) -> dict[str, int]:
    return {k: v for k, v in db.execute(select(coluna, func.count()).group_by(coluna)).all()}


@router.get("/resumo")
def resumo(db: Session = Depends(get_db), _: Usuario = Depends(exigir("painel:ler"))):
    ultimas = db.scalars(select(RegistroAuditoria).order_by(RegistroAuditoria.id.desc()).limit(10)).all()
    return {
        "documentos_total": db.scalar(select(func.count(Documento.id))) or 0,
        "documentos_por_status": _contagem(db, Documento.status),
        "documentos_por_tipo": _contagem(db, Documento.tipo),
        "documentos_por_classificacao": _contagem(db, Documento.classificacao),
        "arquivos_total": db.scalar(select(func.count(Arquivo.id))) or 0,
        "armazenamento_bytes": int(db.scalar(select(func.coalesce(func.sum(Arquivo.tamanho), 0))) or 0),
        "usuarios_ativos": db.scalar(select(func.count(Usuario.id)).where(Usuario.ativo.is_(True))) or 0,
        "usuarios_por_perfil": _contagem(db, Usuario.perfil),
        "ultimas_acoes": [AuditoriaOut.model_validate(r).model_dump(mode="json") for r in ultimas],
    }
