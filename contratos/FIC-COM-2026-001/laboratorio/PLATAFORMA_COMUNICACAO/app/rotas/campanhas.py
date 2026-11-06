"""Campanhas de comunicação."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ..acesso import exigir_perfil, usuario_atual
from ..comum import como_lista, now, registrar_auditoria
from ..db import connect
from ..esquemas import CampanhaNova

router = APIRouter(prefix="/api/campaigns", tags=["campanhas"])


@router.get("")
def listar_campanhas(usuario: dict[str, Any] = Depends(usuario_atual)) -> list[dict[str, Any]]:
    with connect() as c:
        return como_lista(c.execute("SELECT * FROM campaigns ORDER BY id DESC").fetchall())


@router.post("", status_code=201)
def criar_campanha(
    dados: CampanhaNova, usuario: dict[str, Any] = Depends(exigir_perfil("ADMIN", "EDITOR"))
) -> dict[str, Any]:
    with connect() as c:
        if dados.channel_id is not None and not c.execute("SELECT 1 FROM channels WHERE id = ?", (dados.channel_id,)).fetchone():
            raise HTTPException(404, "Canal não encontrado")
        cursor = c.execute(
            "INSERT INTO campaigns (name, objective, channel_id, starts_on, ends_on, owner_id, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (dados.name, dados.objective, dados.channel_id, dados.starts_on, dados.ends_on, usuario["id"], now()),
        )
        registrar_auditoria(c, usuario["id"], "CREATE", "campaign", cursor.lastrowid)
        return {"id": cursor.lastrowid, "status": "PLANEJADA"}
