"""MOD-001 — Autenticação: login, logout, sessão atual, recuperação e redefinição de senha."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .. import mail
from ..audit import registrar
from ..config import config
from ..db import get_db
from ..deps import token_atual, usuario_atual
from ..models import TokenRecuperacao, TokenRevogado, Usuario
from ..schemas import LoginIn, RecuperarIn, RedefinirIn, TokenOut, UsuarioOut
from ..security import (criar_token, hash_senha, hash_token, limitador, novo_token_recuperacao,
                        validar_politica_senha, verificar_senha)

router = APIRouter(prefix="/api/auth", tags=["autenticação"])

# Hash fixo para igualar o tempo de resposta quando o e-mail não existe.
_HASH_FALSO = hash_senha("senha-inexistente-0000")


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


@router.post("/login", response_model=TokenOut)
def login(dados: LoginIn, request: Request, db: Session = Depends(get_db)):
    email = dados.email.strip().lower()
    if limitador.bloqueado(email):
        registrar(db, acao="LOGIN_BLOQUEADO", recurso="auth", recurso_id=email, request=request)
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS,
                            f"Muitas tentativas. Tente novamente em {config.login_bloqueio_min} minutos.")
    u = db.scalar(select(Usuario).where(Usuario.email == email))
    ok = verificar_senha(dados.senha, u.senha_hash if u else _HASH_FALSO)
    if not u or not ok or not u.ativo:
        limitador.falhou(email)
        registrar(db, acao="LOGIN_FALHA", recurso="auth", recurso_id=email, usuario_id=u.id if u else None,
                  request=request)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha inválidos")
    limitador.sucesso(email)
    tok, _, exp = criar_token(u.id, u.perfil, u.versao_sessao)
    registrar(db, acao="LOGIN", recurso="auth", recurso_id=u.id, usuario=u, request=request)
    return TokenOut(access_token=tok, expira_em=exp, usuario=UsuarioOut.model_validate(u))


@router.post("/logout", status_code=204)
def logout(request: Request, payload: dict = Depends(token_atual), u: Usuario = Depends(usuario_atual),
           db: Session = Depends(get_db)):
    db.add(TokenRevogado(jti=payload["jti"], expira_em=datetime.fromtimestamp(payload["exp"], timezone.utc)))
    registrar(db, acao="LOGOUT", recurso="auth", recurso_id=u.id, usuario=u, request=request)


@router.get("/me", response_model=UsuarioOut)
def me(u: Usuario = Depends(usuario_atual)):
    return u


@router.post("/recuperar-senha", status_code=202)
def recuperar_senha(dados: RecuperarIn, request: Request, db: Session = Depends(get_db)):
    """Sempre responde 202 (não revela se o e-mail existe)."""
    email = dados.email.strip().lower()
    chave = f"recuperar:{email}"
    if limitador.bloqueado(chave):  # mesma resposta: não revela nada e não envia e-mail
        return {"mensagem": "Se o e-mail estiver cadastrado, enviaremos as instruções."}
    limitador.falhou(chave)
    u = db.scalar(select(Usuario).where(Usuario.email == email, Usuario.ativo.is_(True)))
    if u:
        db.execute(update(TokenRecuperacao).where(TokenRecuperacao.usuario_id == u.id,
                                                  TokenRecuperacao.usado.is_(False)).values(usado=True))
        bruto, h = novo_token_recuperacao()
        db.add(TokenRecuperacao(usuario_id=u.id, token_hash=h,
                                expira_em=datetime.now(timezone.utc) + timedelta(minutes=30)))
        registrar(db, acao="SENHA_RECUPERACAO_SOLICITADA", recurso="usuario", recurso_id=u.id,
                  usuario_id=u.id, request=request)
        mail.enviar(u.email, "Redefinição de senha",
                    f"Use o link em até 30 minutos: {config.url_publica}/redefinir-senha?token={bruto}")
    return {"mensagem": "Se o e-mail estiver cadastrado, enviaremos as instruções."}


@router.post("/redefinir-senha", status_code=204)
def redefinir_senha(dados: RedefinirIn, request: Request, db: Session = Depends(get_db)):
    erro = validar_politica_senha(dados.nova_senha)
    if erro:
        raise HTTPException(422, erro)
    t = db.scalar(select(TokenRecuperacao).where(TokenRecuperacao.token_hash == hash_token(dados.token)))
    if not t or t.usado or _aware(t.expira_em) < datetime.now(timezone.utc):
        raise HTTPException(400, "Token inválido ou expirado")
    # Marca o token como usado de forma atômica (evita uso duplo simultâneo).
    r = db.execute(update(TokenRecuperacao).where(TokenRecuperacao.id == t.id, TokenRecuperacao.usado.is_(False))
                   .values(usado=True))
    if r.rowcount != 1:
        raise HTTPException(400, "Token inválido ou expirado")
    u = db.get(Usuario, t.usuario_id)
    u.versao_sessao = (u.versao_sessao or 0) + 1  # encerra sessões abertas
    u.senha_hash = hash_senha(dados.nova_senha)
    registrar(db, acao="SENHA_REDEFINIDA", recurso="usuario", recurso_id=u.id, usuario=u, request=request)
