"""Trilha de auditoria (administrador e aprovador)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from ..acesso import exigir_perfil
from ..comum import como_lista
from ..db import connect

router = APIRouter(prefix="/api/audit", tags=["auditoria"])


@router.get("")
def listar_eventos(usuario: dict[str, Any] = Depends(exigir_perfil("ADMIN", "APPROVER"))) -> list[dict[str, Any]]:
    with connect() as c:
        return como_lista(c.execute("SELECT * FROM audit ORDER BY id DESC LIMIT 200").fetchall())
