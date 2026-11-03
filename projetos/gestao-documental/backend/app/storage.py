"""MOD-003 — Armazenamento de arquivos PDF fora do banco, com hash SHA-256."""
from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile

from .config import config

ASSINATURA_PDF = b"%PDF-"
BLOCO = 1024 * 1024


class ArquivoInvalido(ValueError):
    pass


def raiz() -> Path:
    p = Path(config.upload_dir).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def nome_seguro(nome: str) -> str:
    base = os.path.basename(nome or "").replace("\x00", "").strip()
    return base[:255] or "documento.pdf"


async def salvar_pdf(arquivo: UploadFile) -> tuple[str, int, str]:
    """Valida e grava em disco. Retorna (caminho relativo, tamanho, sha256)."""
    nome = nome_seguro(arquivo.filename or "")
    if not nome.lower().endswith(".pdf"):
        raise ArquivoInvalido("Somente arquivos .pdf são aceitos")
    limite = config.max_upload_mb * 1024 * 1024
    agora = datetime.now(timezone.utc)
    rel = Path(f"{agora:%Y}") / f"{agora:%m}" / f"{uuid.uuid4().hex}.pdf"
    destino = raiz() / rel
    destino.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    tamanho = 0
    primeiro = True
    try:
        with open(destino, "wb") as f:
            while bloco := await arquivo.read(BLOCO):
                if primeiro:
                    if not bloco.startswith(ASSINATURA_PDF):
                        raise ArquivoInvalido("O conteúdo não é um PDF válido")
                    primeiro = False
                tamanho += len(bloco)
                if tamanho > limite:
                    raise ArquivoInvalido(f"Arquivo excede o limite de {config.max_upload_mb} MB")
                h.update(bloco)
                f.write(bloco)
        if primeiro:
            raise ArquivoInvalido("Arquivo vazio")
    except BaseException:  # inválido, disco cheio, cancelamento: não deixa arquivo parcial
        destino.unlink(missing_ok=True)
        raise
    return str(rel), tamanho, h.hexdigest()


def caminho_absoluto(rel: str) -> Path:
    p = (raiz() / rel).resolve()
    if raiz() not in p.parents:
        raise ArquivoInvalido("Caminho inválido")
    return p
