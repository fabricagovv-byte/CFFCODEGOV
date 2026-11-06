"""MOD-001 — Gestão de usuários e perfis (somente ADMIN)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..audit import registrar
from ..db import get_db
from ..deps import exigir
from ..models import Usuario
from ..permissions import PERMISSOES
from ..schemas import UsuarioIn, UsuarioOut, UsuarioUpdate
from ..security import hash_senha, validar_politica_senha

router = APIRouter(prefix="/api/usuarios", tags=["usuários"])


@router.get("", response_model=list[UsuarioOut])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(exigir("usuario:gerenciar"))):
    return db.scalars(select(Usuario).order_by(Usuario.nome)).all()


@router.get("/perfis")
def perfis(_: Usuario = Depends(exigir("usuario:gerenciar"))):
    return {p: sorted(v) for p, v in PERMISSOES.items()}


@router.post("", response_model=UsuarioOut, status_code=201)
def criar(dados: UsuarioIn, request: Request, db: Session = Depends(get_db),
          admin: Usuario = Depends(exigir("usuario:gerenciar"))):
    erro = validar_politica_senha(dados.senha)
    if erro:
        raise HTTPException(422, erro)
    email = dados.email.strip().lower()
    if db.scalar(select(Usuario).where(Usuario.email == email)):
        raise HTTPException(409, "E-mail já cadastrado")
    u = Usuario(nome=dados.nome.strip(), email=email, senha_hash=hash_senha(dados.senha), perfil=dados.perfil)
    db.add(u)
    db.flush()
    registrar(db, acao="USUARIO_CRIADO", recurso="usuario", recurso_id=u.id, usuario=admin, request=request,
              detalhes={"perfil": u.perfil})
    return u


@router.patch("/{uid}", response_model=UsuarioOut)
def alterar(uid: int, dados: UsuarioUpdate, request: Request, db: Session = Depends(get_db),
            admin: Usuario = Depends(exigir("usuario:gerenciar"))):
    u = db.get(Usuario, uid)
    if not u:
        raise HTTPException(404, "Usuário não encontrado")
    mud = dados.model_dump(exclude_unset=True, exclude_none=True)
    if u.id == admin.id and (mud.get("ativo") is False or mud.get("perfil", "ADMIN") != "ADMIN"):
        raise HTTPException(400, "Administrador não pode remover o próprio acesso")
    for k, v in mud.items():
        setattr(u, k, v)
    registrar(db, acao="USUARIO_ALTERADO", recurso="usuario", recurso_id=u.id, usuario=admin, request=request,
              detalhes=mud)
    return u
