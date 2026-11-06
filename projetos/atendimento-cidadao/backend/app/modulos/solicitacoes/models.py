"""MOD-103 — Solicitações: modelo de dados (gerado pela fábrica; revise e evolua)."""
from __future__ import annotations

from datetime import date, datetime  # noqa: F401
from decimal import Decimal  # noqa: F401

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text  # noqa: F401
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models import utcnow


class Solicitacao(Base):
    __tablename__ = "solicitacoes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    protocolo: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    cidadao_id: Mapped[int] = mapped_column(ForeignKey("cidadaos.id"), index=True)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"), index=True)
    canal: Mapped[str] = mapped_column(String(30))
    assunto: Mapped[str] = mapped_column(String(200), index=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    situacao: Mapped[str] = mapped_column(String(30))
    prazo: Mapped[date | None] = mapped_column(Date, nullable=True)
    prioritaria: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
