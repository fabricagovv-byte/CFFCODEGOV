"""Canais de comunicação."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from ..acesso import exigir_perfil, usuario_atual
from ..comum import como_lista, now, registrar_auditoria
from ..db import connect
from ..esquemas import CanalNovo

router = APIRouter(prefix="/api/channels", tags=["canais"])


@router.get("")
def listar_canais(usuario: dict[str, Any] = Depends(usuario_atual)) -> list[dict[str, Any]]:
    with connect() as c:
        return como_lista(c.execute("SELECT * FROM channels ORDER BY id DESC").fetchall())


@router.post("", status_code=201)
def criar_canal(dados: CanalNovo, usuario: dict[str, Any] = Depends(exigir_perfil("ADMIN", "EDITOR"))) -> dict[str, Any]:
    with connect() as c:
        cursor = c.execute(
            "INSERT INTO channels (name, description, is_public, created_by, created_at) VALUES (?, ?, ?, ?, ?)",
            (dados.name, dados.description, int(dados.is_public), usuario["id"], now()),
        )
        registrar_auditoria(c, usuario["id"], "CREATE", "channel", cursor.lastrowid)
        return {"id": cursor.lastrowid, "name": dados.name}
