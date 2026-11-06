"""Registro de quem fez o quê."""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from .modelos import Auditoria


def registrar(s: Session, usuario_id: int | None, acao: str, entidade: str, entidade_id: int | None = None,
              detalhe: dict[str, Any] | None = None) -> None:
    s.add(Auditoria(usuario_id=usuario_id, acao=acao, entidade=entidade, entidade_id=entidade_id,
                    detalhe=json.dumps(detalhe or {}, ensure_ascii=False, default=str)))
