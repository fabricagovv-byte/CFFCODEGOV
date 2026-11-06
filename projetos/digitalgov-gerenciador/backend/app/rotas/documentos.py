"""Editais, TR, contratos, OS e termos anexados (PDF, Word, Excel ou imagem)."""
from __future__ import annotations

import hashlib
import re
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import config
from ..acesso import ESCRITA, usuario_atual
from ..auditoria import registrar
from ..db import sessao
from ..modelos import Contrato, Documento, Projeto
from ..serializar import como_dict

router = APIRouter(prefix="/api/documentos", tags=["documentos"])

EXTENSOES = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".odt", ".ods", ".png", ".jpg", ".jpeg", ".txt", ".xml", ".zip"}
TIPOS = {"EDITAL", "TR", "CONTRATO", "OS", "TERMO_ACEITE", "RELATORIO", "OUTRO"}


@router.get("")
def listar(contrato_id: Optional[int] = None, projeto_id: Optional[int] = None,
           s: Session = Depends(sessao), _=Depends(usuario_atual)) -> list[dict]:
    q = select(Documento).order_by(Documento.enviado_em.desc())
    if contrato_id:
        q = q.where(Documento.contrato_id == contrato_id)
    if projeto_id:
        q = q.where(Documento.projeto_id == projeto_id)
    return [como_dict(d) for d in s.scalars(q)]


@router.post("", status_code=201)
async def enviar(tipo: str = Form(...), titulo: str = Form(..., min_length=3), contrato_id: Optional[int] = Form(None),
                 projeto_id: Optional[int] = Form(None), arquivo: UploadFile = File(...),
                 s: Session = Depends(sessao), u=Depends(ESCRITA)) -> dict:
    cfg = config.carregar()
    if tipo not in TIPOS:
        raise HTTPException(422, f"Tipo inválido. Use: {', '.join(sorted(TIPOS))}")
    if not contrato_id and not projeto_id:
        raise HTTPException(422, "Vincule o documento a um contrato ou a um projeto")
    if contrato_id and not s.get(Contrato, contrato_id):
        raise HTTPException(404, "Contrato não encontrado")
    if projeto_id and not s.get(Projeto, projeto_id):
        raise HTTPException(404, "Projeto não encontrado")
    nome = re.sub(r"[^\w.\- ]", "_", arquivo.filename or "arquivo")[:200]
    extensao = ("." + nome.rsplit(".", 1)[-1].lower()) if "." in nome else ""
    if extensao not in EXTENSOES:
        raise HTTPException(422, f"Formato não aceito ({extensao or 'sem extensão'})")
    conteudo = await arquivo.read(cfg.max_upload_mb * 1024 * 1024 + 1)
    if len(conteudo) > cfg.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"Arquivo maior que {cfg.max_upload_mb} MB")
    if not conteudo:
        raise HTTPException(422, "Arquivo vazio")
    cfg.pasta_arquivos.mkdir(parents=True, exist_ok=True)
    destino = cfg.pasta_arquivos / f"{uuid.uuid4().hex}{extensao}"
    destino.write_bytes(conteudo)
    doc = Documento(tipo=tipo, titulo=titulo, contrato_id=contrato_id, projeto_id=projeto_id, nome_arquivo=nome,
                    caminho=destino.name, tamanho=len(conteudo), sha256=hashlib.sha256(conteudo).hexdigest(), enviado_por=u.id)
    s.add(doc)
    s.flush()
    registrar(s, u.id, "ENVIAR", "documento", doc.id, {"tipo": tipo, "arquivo": nome, "sha256": doc.sha256})
    return como_dict(doc)


@router.get("/{documento_id}/arquivo")
def baixar(documento_id: int, s: Session = Depends(sessao), _=Depends(usuario_atual)) -> FileResponse:
    doc = s.get(Documento, documento_id)
    if not doc:
        raise HTTPException(404, "Documento não encontrado")
    caminho = config.carregar().pasta_arquivos / doc.caminho
    if not caminho.is_file() or hashlib.sha256(caminho.read_bytes()).hexdigest() != doc.sha256:
        raise HTTPException(409, "O arquivo guardado não confere com o registro (ausente ou alterado)")
    return FileResponse(caminho, filename=doc.nome_arquivo)
