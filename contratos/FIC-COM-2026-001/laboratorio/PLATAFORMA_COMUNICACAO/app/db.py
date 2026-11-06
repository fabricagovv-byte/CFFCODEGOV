"""Conexão com o banco SQLite. O esquema é criado e atualizado pelas migrações versionadas."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from . import migrations

DB_PATH = Path(os.getenv("DG_COMM_DB", str(Path(__file__).resolve().parents[1] / "data" / "comunicacao.db")))


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(str(DB_PATH), timeout=10, check_same_thread=False)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys=ON")
    return conexao


def init() -> None:
    """Cria ou atualiza o banco aplicando as migrações pendentes."""
    migrations.upgrade(DB_PATH)
