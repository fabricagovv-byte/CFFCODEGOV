"""Registro na trilha de auditoria."""
from __future__ import annotations

import json
import logging

from fastapi import Request
from sqlalchemy.orm import Session

from .models import RegistroAuditoria, Usuario

log = logging.getLogger("gd.auditoria")


def ip_de(request: Request | None) -> str:
    if request is None:
        return ""
    # O IP real vem do proxy confiável (uvicorn --proxy-headers + Nginx que sobrescreve X-Forwarded-For).
    # Nunca ler o cabeçalho bruto aqui: o cliente pode forjá-lo.
    return (request.client.host if request.client else "")[:45]


def registrar(db: Session, *, acao: str, recurso: str, recurso_id: str | int = "",
              usuario: Usuario | None = None, usuario_id: int | None = None,
              request: Request | None = None, detalhes: dict | None = None, commit: bool = True) -> None:
    reg = RegistroAuditoria(
        usuario_id=usuario.id if usuario else usuario_id, acao=acao, recurso=recurso,
        recurso_id=str(recurso_id)[:60], ip=ip_de(request),
        detalhes=json.dumps(detalhes or {}, ensure_ascii=False, default=str))
    db.add(reg)
    if commit:
        db.commit()
    log.info("auditoria acao=%s recurso=%s id=%s usuario=%s", acao, recurso, recurso_id, reg.usuario_id)
