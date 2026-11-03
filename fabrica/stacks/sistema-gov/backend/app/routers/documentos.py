"""MOD-002 — Cadastro documental."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..audit import registrar
from ..db import get_db
from ..deps import exigir
from ..models import Documento, Usuario
from ..permissions import VISIBILIDADE
from ..schemas import DocumentoIn, DocumentoOut, DocumentoUpdate, PaginaDocumentos

router = APIRouter(prefix="/api/documentos", tags=["documentos"])


def obter_visivel(db: Session, did: int, u: Usuario) -> Documento:
    d = db.scalar(select(Documento).options(selectinload(Documento.arquivos)).where(Documento.id == did))
    # 404 também quando não visível: não revela existência de documento restrito.
    if not d or d.classificacao not in VISIBILIDADE[u.perfil]:
        raise HTTPException(404, "Documento não encontrado")
    return d


@router.get("", response_model=PaginaDocumentos)
def listar(pagina: int = Query(1, ge=1), por_pagina: int = Query(20, ge=1, le=100),
           status: str | None = None, tipo: str | None = None,
           db: Session = Depends(get_db), u: Usuario = Depends(exigir("doc:ler"))):
    q = select(Documento).where(Documento.classificacao.in_(VISIBILIDADE[u.perfil]))
    if status:
        q = q.where(Documento.status == status)
    if tipo:
        q = q.where(Documento.tipo == tipo)
    total = db.scalar(select(func.count()).select_from(q.subquery()))
    itens = db.scalars(q.options(selectinload(Documento.arquivos)).order_by(Documento.criado_em.desc(), Documento.id.desc())
                       .offset((pagina - 1) * por_pagina).limit(por_pagina)).all()
    return {"total": total, "pagina": pagina, "por_pagina": por_pagina, "itens": itens}


@router.post("", response_model=DocumentoOut, status_code=201)
def criar(dados: DocumentoIn, request: Request, db: Session = Depends(get_db),
          u: Usuario = Depends(exigir("doc:criar"))):
    if dados.classificacao not in VISIBILIDADE[u.perfil]:
        raise HTTPException(403, "Seu perfil não pode criar documentos com esta classificação")
    d = Documento(**dados.model_dump(), numero=f"tmp-{datetime.now(timezone.utc).timestamp()}", criado_por_id=u.id)
    db.add(d)
    db.flush()
    d.numero = f"{d.criado_em.year if d.criado_em else datetime.now().year}/{d.id:06d}"
    registrar(db, acao="DOCUMENTO_CRIADO", recurso="documento", recurso_id=d.id, usuario=u, request=request,
              detalhes={"numero": d.numero, "classificacao": d.classificacao}, commit=False)
    db.commit()
    db.refresh(d)
    return d


@router.get("/{did}", response_model=DocumentoOut)
def detalhar(did: int, request: Request, db: Session = Depends(get_db), u: Usuario = Depends(exigir("doc:ler"))):
    d = obter_visivel(db, did, u)
    if d.classificacao != "PUBLICO":
        registrar(db, acao="DOCUMENTO_CONSULTADO", recurso="documento", recurso_id=d.id, usuario=u, request=request)
    return d


@router.patch("/{did}", response_model=DocumentoOut)
def alterar(did: int, dados: DocumentoUpdate, request: Request, db: Session = Depends(get_db),
            u: Usuario = Depends(exigir("doc:editar"))):
    d = obter_visivel(db, did, u)
    mud = dados.model_dump(exclude_unset=True, exclude_none=True)  # null = sem alteração
    gestor = u.perfil in ("ADMIN", "GESTOR")
    if d.status == "ARQUIVADO" and not gestor:
        raise HTTPException(403, "Documento arquivado: somente gestor ou administrador altera")
    if "classificacao" in mud and mud["classificacao"] != d.classificacao and not gestor:
        raise HTTPException(403, "Somente gestor ou administrador reclassifica documentos")
    if mud.get("status") == "ARQUIVADO" and not gestor:
        raise HTTPException(403, "Somente gestor ou administrador arquiva documentos")
    antes = {k: getattr(d, k) for k in mud}
    for k, v in mud.items():
        setattr(d, k, v.strip() if isinstance(v, str) else v)
    registrar(db, acao="DOCUMENTO_ALTERADO", recurso="documento", recurso_id=d.id, usuario=u, request=request,
              detalhes={"antes": antes, "depois": mud}, commit=False)
    db.commit()
    db.refresh(d)
    return d


@router.delete("/{did}", status_code=204)
def arquivar(did: int, request: Request, db: Session = Depends(get_db), u: Usuario = Depends(exigir("doc:arquivar"))):
    """Documentos públicos não são apagados: a exclusão lógica muda o status para ARQUIVADO."""
    d = obter_visivel(db, did, u)
    d.status = "ARQUIVADO"
    registrar(db, acao="DOCUMENTO_ARQUIVADO", recurso="documento", recurso_id=d.id, usuario=u, request=request)
