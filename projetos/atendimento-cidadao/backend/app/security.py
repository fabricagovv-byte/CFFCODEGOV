"""Autenticação: hash de senha, JWT com revogação e proteção contra força bruta."""
from __future__ import annotations

import hashlib
import os
import re
import secrets
import threading
import time
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import config

ALG = "HS256"


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt(rounds=int(os.getenv("BCRYPT_ROUNDS", "12")))).decode()


def verificar_senha(senha: str, hash_: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode(), hash_.encode())
    except ValueError:
        return False


def validar_politica_senha(senha: str) -> str | None:
    """Retorna mensagem de erro ou None. Mínimo 10 caracteres com letras e números."""
    if len(senha) < 10:
        return "A senha deve ter pelo menos 10 caracteres"
    if len(senha.encode()) > 72:
        return "A senha deve ter no máximo 72 bytes"
    if not re.search(r"[A-Za-z]", senha) or not re.search(r"\d", senha):
        return "A senha deve conter letras e números"
    return None


def criar_token(usuario_id: int, perfil: str, versao_sessao: int = 0) -> tuple[str, str, datetime]:
    jti = secrets.token_hex(16)
    exp = datetime.now(timezone.utc) + timedelta(minutes=config.jwt_expira_min)
    tok = jwt.encode({"sub": str(usuario_id), "perfil": perfil, "jti": jti, "exp": exp, "sv": versao_sessao,
                      "iat": datetime.now(timezone.utc)}, config.jwt_secret, algorithm=ALG)
    return tok, jti, exp


def decodificar_token(token: str) -> dict:
    return jwt.decode(token, config.jwt_secret, algorithms=[ALG], options={"require": ["exp", "sub", "jti"]})


def novo_token_recuperacao() -> tuple[str, str]:
    bruto = secrets.token_urlsafe(32)
    return bruto, hashlib.sha256(bruto.encode()).hexdigest()


def hash_token(bruto: str) -> str:
    return hashlib.sha256(bruto.encode()).hexdigest()


class LimitadorLogin:
    """Bloqueia o e-mail após N falhas em sequência por M minutos (memória do processo).

    Em produção com várias réplicas, substituir por armazenamento compartilhado (Redis).
    """

    def __init__(self) -> None:
        self._falhas: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def bloqueado(self, chave: str) -> bool:
        janela = config.login_bloqueio_min * 60
        with self._lock:
            tent = [t for t in self._falhas.get(chave, []) if time.monotonic() - t < janela]
            self._falhas[chave] = tent
            return len(tent) >= config.login_max_tentativas

    def falhou(self, chave: str) -> None:
        with self._lock:
            if len(self._falhas) > 50_000:  # limita memória contra chaves aleatórias
                self._falhas.clear()
            self._falhas.setdefault(chave, []).append(time.monotonic())

    def sucesso(self, chave: str) -> None:
        with self._lock:
            self._falhas.pop(chave, None)

    def limpar(self) -> None:
        with self._lock:
            self._falhas.clear()


limitador = LimitadorLogin()
