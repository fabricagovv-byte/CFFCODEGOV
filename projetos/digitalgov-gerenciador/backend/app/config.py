"""Configuração por variáveis de ambiente (nenhuma senha fica no código)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

RAIZ_BACKEND = Path(__file__).resolve().parents[1]
RAIZ_PROJETO = RAIZ_BACKEND.parent


@dataclass(frozen=True)
class Config:
    database_url: str
    pasta_arquivos: Path
    pasta_projetos: Path
    max_upload_mb: int
    jornada_horas: float
    sessao_horas: int


def carregar() -> Config:
    url = os.getenv("GERENCIADOR_DATABASE_URL", "")
    if not url:
        raise RuntimeError("Defina GERENCIADOR_DATABASE_URL (veja .env.example e docs/MANUAL_BANCO_DE_DADOS.md)")
    return Config(
        database_url=url,
        pasta_arquivos=Path(os.getenv("GERENCIADOR_ARQUIVOS", str(RAIZ_PROJETO / "dados" / "arquivos"))),
        pasta_projetos=Path(os.getenv("GERENCIADOR_PROJETOS_DIR", str(RAIZ_PROJETO.parent))),
        max_upload_mb=int(os.getenv("GERENCIADOR_MAX_UPLOAD_MB", "25")),
        jornada_horas=float(os.getenv("GERENCIADOR_JORNADA_HORAS", "8")),
        sessao_horas=int(os.getenv("GERENCIADOR_SESSAO_HORAS", "8")),
    )
