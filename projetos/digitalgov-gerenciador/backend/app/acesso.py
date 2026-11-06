"""Login, sessão no servidor, limite de tentativas e perfis de acesso."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import config
from .auditoria import registrar
from .db import sessao
from .modelos import Sessao, TentativaLogin, Usuario
from .seguranca import conferir_senha, novo_token, resumo_token

MAX_FALHAS = 5
JANELA_MINUTOS = 15

router = APIRouter(prefix="/api", tags=["acesso"])


class DadosLogin(BaseModel):
    login: str
    senha: str


def usuario_atual(authorization: str | None = Header(default=None), s: Session = Depends(sessao)) -> Usuario:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Faça login para continuar")
    registro = s.scalar(select(Sessao).where(Sessao.token_hash == resumo_token(authorization[7:])))
    if not registro or registro.encerrada_em or registro.expira_em < datetime.now(timezone.utc):
        raise HTTPException(401, "Sessão encerrada ou expirada")
    usuario = s.get(Usuario, registro.usuario_id)
    if not usuario or not usuario.ativo:
        raise HTTPException(401, "Usuário inativo")
    usuario.sessao_id = registro.id  # type: ignore[attr-defined]
    return usuario


def exigir_perfil(*perfis: str) -> Callable[..., Usuario]:
    def conferir(usuario: Usuario = Depends(usuario_atual)) -> Usuario:
        if usuario.perfil not in perfis:
            raise HTTPException(403, "Seu perfil não permite esta ação")
        return usuario
    return conferir


ESCRITA = exigir_perfil("ADMIN", "GESTOR")
SO_ADMIN = exigir_perfil("ADMIN")


@router.post("/login")
def login(dados: DadosLogin, s: Session = Depends(sessao)) -> dict:
    agora = datetime.now(timezone.utc)
    ultimo_acerto = s.scalar(select(func.max(TentativaLogin.em)).where(TentativaLogin.login == dados.login,
                                                                       TentativaLogin.sucesso.is_(True)))
    desde = max(agora - timedelta(minutes=JANELA_MINUTOS), ultimo_acerto or agora - timedelta(days=1))
    falhas = s.scalar(select(func.count()).select_from(TentativaLogin).where(
        TentativaLogin.login == dados.login, TentativaLogin.sucesso.is_(False), TentativaLogin.em > desde))
    if falhas >= MAX_FALHAS:
        registrar(s, None, "LOGIN_BLOQUEADO", "usuario", None, {"login": dados.login})
        s.commit()
        raise HTTPException(429, f"Muitas tentativas. Tente de novo em {JANELA_MINUTOS} minutos")

    usuario = s.scalar(select(Usuario).where(Usuario.login == dados.login, Usuario.ativo.is_(True)))
    certo = bool(usuario) and conferir_senha(dados.senha, usuario.senha_hash)
    s.add(TentativaLogin(login=dados.login, sucesso=certo, em=agora))
    if not certo:
        registrar(s, None, "LOGIN_FALHOU", "usuario", None, {"login": dados.login})
        s.commit()
        raise HTTPException(401, "Login ou senha incorretos")

    token = novo_token()
    s.add(Sessao(usuario_id=usuario.id, token_hash=resumo_token(token),
                 expira_em=agora + timedelta(hours=config.carregar().sessao_horas)))
    registrar(s, usuario.id, "LOGIN", "usuario", usuario.id)
    return {"token": token, "nome": usuario.nome, "perfil": usuario.perfil}


@router.post("/logout")
def logout(usuario: Usuario = Depends(usuario_atual), s: Session = Depends(sessao)) -> dict:
    registro = s.get(Sessao, usuario.sessao_id)  # type: ignore[attr-defined]
    registro.encerrada_em = datetime.now(timezone.utc)
    registrar(s, usuario.id, "LOGOUT", "usuario", usuario.id)
    return {"situacao": "sessão encerrada"}


@router.get("/eu")
def eu(usuario: Usuario = Depends(usuario_atual)) -> dict:
    return {"id": usuario.id, "nome": usuario.nome, "login": usuario.login, "perfil": usuario.perfil}
