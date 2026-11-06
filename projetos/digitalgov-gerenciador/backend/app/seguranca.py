"""Senhas com scrypt e tokens de sessão aleatórios (o banco guarda só o resumo SHA-256 do token)."""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

_N, _R, _P = 2**14, 8, 1
TAMANHO_MINIMO_SENHA = 12


def gerar_hash_senha(senha: str) -> str:
    if len(senha) < TAMANHO_MINIMO_SENHA:
        raise ValueError(f"A senha precisa ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres")
    sal = secrets.token_bytes(16)
    resumo = hashlib.scrypt(senha.encode(), salt=sal, n=_N, r=_R, p=_P)
    return f"scrypt${_N}${_R}${_P}${base64.b64encode(sal).decode()}${base64.b64encode(resumo).decode()}"


def conferir_senha(senha: str, guardada: str) -> bool:
    try:
        _, n, r, p, sal, resumo = guardada.split("$")
        teste = hashlib.scrypt(senha.encode(), salt=base64.b64decode(sal), n=int(n), r=int(r), p=int(p))
        return hmac.compare_digest(teste, base64.b64decode(resumo))
    except (ValueError, TypeError):
        return False


def novo_token() -> str:
    return secrets.token_urlsafe(32)


def resumo_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
