"""Tabelas do projeto. Substitua 'registros' pelas tabelas de negócio exigidas no contrato."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def agora() -> datetime:
    return datetime.now(timezone.utc)


class Registro(Base):
    __tablename__ = "registros"
    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    descricao: Mapped[str | None] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)


class CicloProducao(Base):
    """Cada START recebido do gerenciador central."""
    __tablename__ = "ciclos_producao"
    id: Mapped[int] = mapped_column(primary_key=True)
    iniciado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    origem: Mapped[str] = mapped_column(String(60), default="gerenciador")
