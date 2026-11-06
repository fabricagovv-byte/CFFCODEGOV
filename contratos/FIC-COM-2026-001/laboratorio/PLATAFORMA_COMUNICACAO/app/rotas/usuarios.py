"""Cadastro de usuários (somente administrador)."""
from __future__ import annotations

import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ..acesso import exigir_perfil
from ..comum import now, registrar_auditoria
from ..db import connect
from ..esquemas import UsuarioNovo
from ..security import hash_password

router = APIRouter(prefix="/api/users", tags=["usuários"])


@router.post("", status_code=201)
def criar_usuario(dados: UsuarioNovo, usuario: dict[str, Any] = Depends(exigir_perfil("ADMIN"))) -> dict[str, Any]:
    try:
        with connect() as c:
            cursor = c.execute(
                "INSERT INTO users (name, username, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
                (dados.name, dados.username, hash_password(dados.password), dados.role, now()),
            )
            registrar_auditoria(c, usuario["id"], "CREATE", "user", cursor.lastrowid)
            return {"id": cursor.lastrowid, "username": dados.username, "role": dados.role}
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Usuário duplicado")
