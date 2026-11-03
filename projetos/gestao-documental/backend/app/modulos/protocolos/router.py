"""MOD-102 — Protocolos: API REST (listar, detalhar, criar, alterar, excluir logicamente)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, or_, select, text  # noqa: F401
from sqlalchemy.orm import Session

from app.audit import registrar
from app.db import get_db
from app.deps import exigir_perfil
from app.models import Usuario

from .models import Protocolo
from .schemas import ProtocoloIn, ProtocoloOut, ProtocoloUpdate, PaginaProtocolo

router = APIRouter(prefix="/api/protocolos", tags=["Protocolos"])
LER = ('ADMIN', 'GESTOR', 'OPERADOR', 'CONSULTA')
ESCREVER = ('ADMIN', 'GESTOR', 'OPERADOR')
EXCLUIR = ('ADMIN', 'GESTOR')
CAMPOS_PESSOAIS = set()  # não vão para os detalhes da auditoria (LGPD)
UNICOS = ['numero']
REFERENCIAS = {'interessado_id': 'interessados'}


def _escapar(t: str) -> str:
    return t.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _auditavel(d: dict) -> dict:
    return {k: ('***' if k in CAMPOS_PESSOAIS else v) for k, v in d.items()}


def _obter(db: Session, rid: int) -> Protocolo:
    obj = db.get(Protocolo, rid)
    if not obj:
        raise HTTPException(404, "Protocolos: registro não encontrado")
    return obj


def _validar(db: Session, dados: dict, rid: int | None = None) -> None:
    for campo in UNICOS:
        if dados.get(campo) is not None:
            q = select(Protocolo.id).where(getattr(Protocolo, campo) == dados[campo])
            if rid:
                q = q.where(Protocolo.id != rid)
            if db.scalar(q):
                raise HTTPException(409, f"Já existe registro com este {campo}")
    for campo, alvo in REFERENCIAS.items():
        if dados.get(campo) is not None:
            if not db.execute(text(f"SELECT 1 FROM {alvo} WHERE id = :i"), {"i": dados[campo]}).first():
                raise HTTPException(422, f"{campo}: registro relacionado não existe")


@router.get("", response_model=PaginaProtocolo)
def listar(q: str = Query("", max_length=200), pagina: int = Query(1, ge=1), por_pagina: int = Query(20, ge=1, le=100),
           incluir_inativos: bool = False, db: Session = Depends(get_db), _: Usuario = Depends(exigir_perfil(*LER))):
    consulta = select(Protocolo)
    if not incluir_inativos:
        consulta = consulta.where(Protocolo.ativo.is_(True))
    for termo in q.split():
        padrao = f"%{_escapar(termo.lower())}%"
        consulta = consulta.where(or_(func.lower(Protocolo.numero).like(padrao, escape="\\"), func.lower(Protocolo.assunto).like(padrao, escape="\\")))
    total = db.scalar(select(func.count()).select_from(consulta.subquery()))
    itens = db.scalars(consulta.order_by(Protocolo.id.desc()).offset((pagina - 1) * por_pagina).limit(por_pagina)).all()
    return {"total": total, "pagina": pagina, "por_pagina": por_pagina, "itens": itens}


@router.get("/{rid}", response_model=ProtocoloOut)
def detalhar(rid: int, db: Session = Depends(get_db), _: Usuario = Depends(exigir_perfil(*LER))):
    return _obter(db, rid)


@router.post("", response_model=ProtocoloOut, status_code=201)
def criar(dados: ProtocoloIn, request: Request, db: Session = Depends(get_db), u: Usuario = Depends(exigir_perfil(*ESCREVER))):
    d = dados.model_dump()
    _validar(db, d)
    obj = Protocolo(**d)
    db.add(obj)
    db.flush()
    registrar(db, acao="PROTOCOLOS_CRIADO", recurso="protocolos", recurso_id=obj.id, usuario=u, request=request,
              detalhes=_auditavel(d), commit=False)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{rid}", response_model=ProtocoloOut)
def alterar(rid: int, dados: ProtocoloUpdate, request: Request, db: Session = Depends(get_db),
            u: Usuario = Depends(exigir_perfil(*ESCREVER))):
    obj = _obter(db, rid)
    mud = dados.model_dump(exclude_unset=True, exclude_none=True)
    _validar(db, mud, rid)
    antes = {k: getattr(obj, k) for k in mud}
    for k, v in mud.items():
        setattr(obj, k, v)
    registrar(db, acao="PROTOCOLOS_ALTERADO", recurso="protocolos", recurso_id=obj.id, usuario=u, request=request,
              detalhes={"antes": _auditavel(antes), "depois": _auditavel(mud)}, commit=False)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{rid}", status_code=204)
def excluir(rid: int, request: Request, db: Session = Depends(get_db), u: Usuario = Depends(exigir_perfil(*EXCLUIR))):
    """Exclusão lógica: o registro fica inativo e continua na base (rastreabilidade)."""
    obj = _obter(db, rid)
    obj.ativo = False
    registrar(db, acao="PROTOCOLOS_EXCLUIDO", recurso="protocolos", recurso_id=obj.id, usuario=u, request=request)
