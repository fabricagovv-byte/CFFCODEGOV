"""MOD-102 — Cidadãos: API REST (listar, detalhar, criar, alterar, excluir logicamente)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, or_, select, text  # noqa: F401
from sqlalchemy.orm import Session

from app.audit import registrar
from app.db import get_db
from app.deps import exigir_perfil
from app.models import Usuario

from .models import Cidadao
from .schemas import CidadaoIn, CidadaoOut, CidadaoUpdate, PaginaCidadao

router = APIRouter(prefix="/api/cidadaos", tags=["Cidadãos"])
LER = ('ADMIN', 'GESTOR', 'OPERADOR', 'CONSULTA')
ESCREVER = ('ADMIN', 'GESTOR', 'OPERADOR')
EXCLUIR = ('ADMIN', 'GESTOR')
CAMPOS_PESSOAIS = {'telefone', 'cpf', 'data_nascimento', 'email'}  # não vão para os detalhes da auditoria (LGPD)
UNICOS = ['cpf']
REFERENCIAS = {}


def _escapar(t: str) -> str:
    return t.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _auditavel(d: dict) -> dict:
    return {k: ('***' if k in CAMPOS_PESSOAIS else v) for k, v in d.items()}


def _obter(db: Session, rid: int) -> Cidadao:
    obj = db.get(Cidadao, rid)
    if not obj:
        raise HTTPException(404, "Cidadãos: registro não encontrado")
    return obj


def _validar(db: Session, dados: dict, rid: int | None = None) -> None:
    for campo in UNICOS:
        if dados.get(campo) is not None:
            q = select(Cidadao.id).where(getattr(Cidadao, campo) == dados[campo])
            if rid:
                q = q.where(Cidadao.id != rid)
            if db.scalar(q):
                raise HTTPException(409, f"Já existe registro com este {campo}")
    for campo, alvo in REFERENCIAS.items():
        if dados.get(campo) is not None:
            if not db.execute(text(f"SELECT 1 FROM {alvo} WHERE id = :i"), {"i": dados[campo]}).first():
                raise HTTPException(422, f"{campo}: registro relacionado não existe")


@router.get("", response_model=PaginaCidadao)
def listar(q: str = Query("", max_length=200), pagina: int = Query(1, ge=1), por_pagina: int = Query(20, ge=1, le=100),
           incluir_inativos: bool = False, db: Session = Depends(get_db), _: Usuario = Depends(exigir_perfil(*LER))):
    consulta = select(Cidadao)
    if not incluir_inativos:
        consulta = consulta.where(Cidadao.ativo.is_(True))
    for termo in q.split():
        padrao = f"%{_escapar(termo.lower())}%"
        consulta = consulta.where(or_(func.lower(Cidadao.nome).like(padrao, escape="\\"), func.lower(Cidadao.cpf).like(padrao, escape="\\")))
    total = db.scalar(select(func.count()).select_from(consulta.subquery()))
    itens = db.scalars(consulta.order_by(Cidadao.id.desc()).offset((pagina - 1) * por_pagina).limit(por_pagina)).all()
    return {"total": total, "pagina": pagina, "por_pagina": por_pagina, "itens": itens}


@router.get("/{rid}", response_model=CidadaoOut)
def detalhar(rid: int, db: Session = Depends(get_db), _: Usuario = Depends(exigir_perfil(*LER))):
    return _obter(db, rid)


@router.post("", response_model=CidadaoOut, status_code=201)
def criar(dados: CidadaoIn, request: Request, db: Session = Depends(get_db), u: Usuario = Depends(exigir_perfil(*ESCREVER))):
    d = dados.model_dump()
    _validar(db, d)
    obj = Cidadao(**d)
    db.add(obj)
    db.flush()
    registrar(db, acao="CIDADAOS_CRIADO", recurso="cidadaos", recurso_id=obj.id, usuario=u, request=request,
              detalhes=_auditavel(d), commit=False)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{rid}", response_model=CidadaoOut)
def alterar(rid: int, dados: CidadaoUpdate, request: Request, db: Session = Depends(get_db),
            u: Usuario = Depends(exigir_perfil(*ESCREVER))):
    obj = _obter(db, rid)
    mud = dados.model_dump(exclude_unset=True, exclude_none=True)
    _validar(db, mud, rid)
    antes = {k: getattr(obj, k) for k in mud}
    for k, v in mud.items():
        setattr(obj, k, v)
    registrar(db, acao="CIDADAOS_ALTERADO", recurso="cidadaos", recurso_id=obj.id, usuario=u, request=request,
              detalhes={"antes": _auditavel(antes), "depois": _auditavel(mud)}, commit=False)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{rid}", status_code=204)
def excluir(rid: int, request: Request, db: Session = Depends(get_db), u: Usuario = Depends(exigir_perfil(*EXCLUIR))):
    """Exclusão lógica: o registro fica inativo e continua na base (rastreabilidade)."""
    obj = _obter(db, rid)
    obj.ativo = False
    registrar(db, acao="CIDADAOS_EXCLUIDO", recurso="cidadaos", recurso_id=obj.id, usuario=u, request=request)
