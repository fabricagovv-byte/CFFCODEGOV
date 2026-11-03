"""MOD-003 — Upload e download de PDF."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..audit import registrar
from ..db import get_db
from ..deps import exigir
from ..models import Arquivo, Usuario
from ..permissions import VISIBILIDADE
from ..schemas import ArquivoOut
from ..storage import ArquivoInvalido, caminho_absoluto, nome_seguro, salvar_pdf
from .documentos import obter_visivel

router = APIRouter(prefix="/api", tags=["arquivos"])


@router.post("/documentos/{did}/arquivos", response_model=ArquivoOut, status_code=201)
async def enviar(did: int, request: Request, arquivo: UploadFile = File(...), db: Session = Depends(get_db),
                 u: Usuario = Depends(exigir("arquivo:enviar"))):
    d = obter_visivel(db, did, u)
    if d.status == "ARQUIVADO":
        raise HTTPException(409, "Documento arquivado não recebe anexos")
    try:
        rel, tamanho, sha = await salvar_pdf(arquivo)
    except ArquivoInvalido as e:
        registrar(db, acao="UPLOAD_REJEITADO", recurso="documento", recurso_id=d.id, usuario=u, request=request,
                  detalhes={"motivo": str(e), "nome": arquivo.filename})
        raise HTTPException(422, str(e))
    a = Arquivo(documento_id=d.id, nome_original=nome_seguro(arquivo.filename or ""), caminho=rel,
                tamanho=tamanho, sha256=sha, enviado_por_id=u.id)
    db.add(a)
    db.flush()
    registrar(db, acao="ARQUIVO_ENVIADO", recurso="arquivo", recurso_id=a.id, usuario=u, request=request,
              detalhes={"documento": d.id, "sha256": sha, "tamanho": tamanho}, commit=False)
    try:
        db.commit()
    except Exception:
        db.rollback()
        caminho_absoluto(rel).unlink(missing_ok=True)  # não deixa arquivo órfão
        raise
    db.refresh(a)
    return a


@router.get("/arquivos/{aid}")
def baixar(aid: int, request: Request, db: Session = Depends(get_db), u: Usuario = Depends(exigir("arquivo:baixar"))):
    a = db.get(Arquivo, aid)
    if not a or a.documento.classificacao not in VISIBILIDADE[u.perfil]:
        raise HTTPException(404, "Arquivo não encontrado")
    p = caminho_absoluto(a.caminho)
    if not p.exists():
        raise HTTPException(410, "Arquivo indisponível no armazenamento")
    registrar(db, acao="ARQUIVO_BAIXADO", recurso="arquivo", recurso_id=a.id, usuario=u, request=request)
    return FileResponse(p, media_type="application/pdf", filename=a.nome_original)
