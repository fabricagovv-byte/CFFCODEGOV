from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .db import get_db
from .models import TokenRevogado, Usuario
from .permissions import tem
from .security import decodificar_token

bearer = HTTPBearer(auto_error=False)


def _nao_autorizado(msg: str = "Não autenticado") -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, msg, headers={"WWW-Authenticate": "Bearer"})


def token_atual(cred: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if cred is None:
        raise _nao_autorizado()
    try:
        return decodificar_token(cred.credentials)
    except jwt.PyJWTError:
        raise _nao_autorizado("Token inválido ou expirado")


def usuario_atual(payload: dict = Depends(token_atual), db: Session = Depends(get_db)) -> Usuario:
    if db.get(TokenRevogado, payload["jti"]):
        raise _nao_autorizado("Sessão encerrada")
    u = db.get(Usuario, int(payload["sub"]))
    if not u or not u.ativo:
        raise _nao_autorizado("Usuário inativo")
    if payload.get("sv", 0) != u.versao_sessao:
        raise _nao_autorizado("Sessão encerrada após troca de senha")
    return u


def exigir(permissao: str) -> Callable[[Usuario], Usuario]:
    def _dep(u: Usuario = Depends(usuario_atual)) -> Usuario:
        if not tem(u.perfil, permissao):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Permissão insuficiente")
        return u
    return _dep


def exigir_perfil(*perfis: str) -> Callable[[Usuario], Usuario]:
    """Permite só os perfis informados (usado pelos módulos gerados)."""
    def _dep(u: Usuario = Depends(usuario_atual)) -> Usuario:
        if u.perfil not in perfis:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Permissão insuficiente")
        return u
    return _dep


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)
