"""Funções usadas por todas as rotas: data/hora, conversão de linhas e trilha de auditoria."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any


def now() -> str:
    """Data e hora atuais em UTC, formato ISO 8601."""
    return datetime.now(timezone.utc).isoformat()


def como_dict(linha: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(linha) if linha else None


def como_lista(linhas: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(linha) for linha in linhas]


def registrar_auditoria(
    conexao: sqlite3.Connection,
    usuario_id: int | None,
    acao: str,
    entidade: str,
    entidade_id: int | None,
    detalhe: dict[str, Any] | None = None,
) -> None:
    conexao.execute(
        "INSERT INTO audit (user_id, action, entity, entity_id, at, detail) VALUES (?, ?, ?, ?, ?, ?)",
        (usuario_id, acao, entidade, entidade_id, now(), json.dumps(detalhe or {}, ensure_ascii=False)),
    )
