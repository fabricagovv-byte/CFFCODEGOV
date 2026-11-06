"""Usuários do gerenciador (só administrador)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..acesso import SO_ADMIN
from ..auditoria import registrar
from ..db import sessao
from ..esquemas import UsuarioNovo
from ..modelos import Usuario
from ..seguranca import gerar_hash_senha
from ..serializar import como_dict

router = APIRouter(prefix="/api/usuarios", tags=["usuários"])


@router.get("")
def listar(s: Session = Depends(sessao), _=Depends(SO_ADMIN)) -> list[dict]:
    return [como_dict(u) for u in s.scalars(select(Usuario).order_by(Usuario.nome))]


@router.post("", status_code=201)
def criar(dados: UsuarioNovo, s: Session = Depends(sessao), u=Depends(SO_ADMIN)) -> dict:
    if s.scalar(select(Usuario).where(Usuario.login == dados.login)):
        raise HTTPException(409, "Já existe usuário com este login")
    novo = Usuario(nome=dados.nome, login=dados.login, perfil=dados.perfil, senha_hash=gerar_hash_senha(dados.senha))
    s.add(novo)
    s.flush()
    registrar(s, u.id, "CRIAR", "usuario", novo.id, {"login": dados.login, "perfil": dados.perfil})
    return como_dict(novo)
