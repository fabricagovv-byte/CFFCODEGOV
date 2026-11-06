"""Indicadores da visão geral, calculados no banco."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from ..acesso import usuario_atual
from ..db import connect

router = APIRouter(prefix="/api", tags=["painel"])

TABELAS_CONTADAS = ("channels", "posts", "campaigns", "contacts", "tickets", "deliveries")


@router.get("/overview")
def visao_geral(usuario: dict[str, Any] = Depends(usuario_atual)) -> dict[str, Any]:
    with connect() as c:
        def contar(sql: str) -> int:
            return c.execute(sql).fetchone()[0]

        indicadores = {tabela: contar(f"SELECT COUNT(*) FROM {tabela}") for tabela in TABELAS_CONTADAS}
        publicadas = contar("SELECT COUNT(*) FROM posts WHERE status = 'PUBLICADO'")
        if usuario["role"] == "VIEWER":
            indicadores["posts"] = publicadas
        indicadores["posts_published"] = publicadas
        indicadores["tickets_open"] = contar("SELECT COUNT(*) FROM tickets WHERE status != 'RESOLVIDO'")
    return {"kpis": indicadores, "note": "Indicadores provenientes do banco de dados; nenhuma entrega externa é simulada"}
