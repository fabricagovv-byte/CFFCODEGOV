"""Senhas (PBKDF2-SHA256) e tokens de sessão assinados com HMAC-SHA256."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

SECRET = os.getenv("DG_COMM_SECRET", "")
SESSAO_HORAS = 8
ITERACOES_PBKDF2 = 260_000
TAMANHO_MINIMO_SENHA = 12


def hash_password(senha: str) -> str:
    if len(senha) < TAMANHO_MINIMO_SENHA:
        raise ValueError(f"A senha precisa ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres")
    sal = secrets.token_bytes(16)
    resumo = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal, ITERACOES_PBKDF2)
    return "pbkdf2$" + base64.b64encode(sal).decode() + "$" + base64.b64encode(resumo).decode()


def verify_password(senha: str, armazenada: str) -> bool:
    try:
        _, sal, resumo = armazenada.split("$")
        teste = hashlib.pbkdf2_hmac("sha256", senha.encode(), base64.b64decode(sal), ITERACOES_PBKDF2)
        return hmac.compare_digest(teste, base64.b64decode(resumo))
    except (ValueError, TypeError):
        return False


def new_session_id() -> str:
    return secrets.token_urlsafe(24)


def _assinar(corpo: str) -> str:
    return hmac.new(SECRET.encode(), corpo.encode(), "sha256").hexdigest()


def token_for(usuario_id: int, sessao_id: str) -> str:
    """Token com usuário, sessão e validade. A sessão é conferida no banco a cada requisição."""
    if len(SECRET) < 32:
        raise RuntimeError("DG_COMM_SECRET obrigatório, 32+ caracteres")
    dados = {"uid": usuario_id, "sid": sessao_id, "exp": int(time.time()) + SESSAO_HORAS * 3600}
    corpo = base64.urlsafe_b64encode(json.dumps(dados, separators=(",", ":")).encode()).decode().rstrip("=")
    return f"{corpo}.{_assinar(corpo)}"


def decode(token: str) -> dict | None:
    """Devolve {'uid', 'sid'} quando a assinatura e a validade conferem; senão None."""
    if len(SECRET) < 32:
        return None
    try:
        corpo, assinatura = token.split(".", 1)
        if not hmac.compare_digest(assinatura, _assinar(corpo)):
            return None
        dados = json.loads(base64.urlsafe_b64decode(corpo + "=" * (-len(corpo) % 4)))
        if dados.get("exp", 0) < time.time() or not dados.get("sid"):
            return None
        return {"uid": int(dados["uid"]), "sid": str(dados["sid"])}
    except (ValueError, IndexError, TypeError, KeyError):
        return None
