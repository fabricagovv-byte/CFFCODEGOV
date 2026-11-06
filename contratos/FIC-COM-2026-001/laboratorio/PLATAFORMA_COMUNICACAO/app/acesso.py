"""Sessão do usuário: login com limite de tentativas, saída e conferência de perfil em cada rota."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from .comum import como_dict, now, registrar_auditoria
from .db import connect
from .esquemas import Login
from .security import SESSAO_HORAS, decode, new_session_id, token_for, verify_password

MAX_FALHAS_POR_USUARIO = 5
MAX_FALHAS_POR_IP = 20
JANELA_MINUTOS = 15

router = APIRouter(prefix="/api", tags=["acesso"])


def usuario_atual(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Autenticação obrigatória")
    token = decode(authorization[7:])
    if not token:
        raise HTTPException(401, "Token inválido ou expirado")
    with connect() as c:
        sessao = c.execute("SELECT * FROM sessions WHERE id = ? AND user_id = ?", (token["sid"], token["uid"])).fetchone()
        if not sessao or sessao["revoked_at"] or sessao["expires_at"] < now():
            raise HTTPException(401, "Sessão encerrada ou expirada")
        usuario = c.execute(
            "SELECT id, name, username, role FROM users WHERE id = ? AND active = 1", (token["uid"],)
        ).fetchone()
    if not usuario:
        raise HTTPException(401, "Usuário não encontrado")
    return {**como_dict(usuario), "sid": token["sid"]}


def exigir_perfil(*perfis: str) -> Callable[..., dict[str, Any]]:
    def conferir(usuario: dict[str, Any] = Depends(usuario_atual)) -> dict[str, Any]:
        if usuario["role"] not in perfis:
            raise HTTPException(403, "Acesso não permitido")
        return usuario

    return conferir


def _falhas_recentes(c: sqlite3.Connection, campo: str, valor: str, desde: str) -> int:
    """Senhas erradas na janela, contadas depois do último acesso certo."""
    ultimo_acerto = c.execute(
        f"SELECT MAX(at) FROM login_attempts WHERE {campo} = ? AND success = 1", (valor,)
    ).fetchone()[0] or ""
    return c.execute(
        f"SELECT COUNT(*) FROM login_attempts WHERE {campo} = ? AND success = 0 AND at >= ? AND at > ?",
        (valor, desde, ultimo_acerto),
    ).fetchone()[0]


@router.post("/login")
def login(dados: Login, request: Request) -> dict[str, Any]:
    ip = request.client.host if request.client else "desconhecido"
    desde = (datetime.now(timezone.utc) - timedelta(minutes=JANELA_MINUTOS)).isoformat()
    with connect() as c:
        bloqueado = (
            _falhas_recentes(c, "username", dados.username, desde) >= MAX_FALHAS_POR_USUARIO
            or _falhas_recentes(c, "ip", ip, desde) >= MAX_FALHAS_POR_IP
        )
        if bloqueado:
            registrar_auditoria(c, None, "LOGIN_BLOQUEADO", "user", None, {"username": dados.username, "ip": ip})
            c.commit()  # grava antes do erro, que desfaria a transação
            raise HTTPException(429, f"Muitas tentativas de acesso; tente novamente em {JANELA_MINUTOS} minutos")

        usuario = c.execute("SELECT * FROM users WHERE username = ? AND active = 1", (dados.username,)).fetchone()
        senha_certa = bool(usuario) and verify_password(dados.password, usuario["password_hash"])
        c.execute(
            "INSERT INTO login_attempts (username, ip, success, at) VALUES (?, ?, ?, ?)",
            (dados.username, ip, int(senha_certa), now()),
        )
        if not senha_certa:
            registrar_auditoria(c, None, "LOGIN_FALHOU", "user", None, {"username": dados.username, "ip": ip})
            c.commit()
            raise HTTPException(401, "Credenciais inválidas")

        sessao_id = new_session_id()
        inicio = datetime.now(timezone.utc)
        c.execute(
            "INSERT INTO sessions (id, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (sessao_id, usuario["id"], inicio.isoformat(), (inicio + timedelta(hours=SESSAO_HORAS)).isoformat()),
        )
        registrar_auditoria(c, usuario["id"], "LOGIN_OK", "user", usuario["id"], {"ip": ip})
        return {"token": token_for(usuario["id"], sessao_id), "role": usuario["role"], "name": usuario["name"]}


@router.post("/logout")
def logout(usuario: dict[str, Any] = Depends(usuario_atual)) -> dict[str, str]:
    with connect() as c:
        c.execute("UPDATE sessions SET revoked_at = ? WHERE id = ?", (now(), usuario["sid"]))
        registrar_auditoria(c, usuario["id"], "LOGOUT", "user", usuario["id"])
    return {"status": "SESSAO_ENCERRADA"}


@router.get("/me")
def me(usuario: dict[str, Any] = Depends(usuario_atual)) -> dict[str, Any]:
    return {chave: valor for chave, valor in usuario.items() if chave != "sid"}
