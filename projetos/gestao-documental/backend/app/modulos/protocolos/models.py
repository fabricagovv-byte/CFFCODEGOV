"""MOD-102 — Protocolos: modelo de dados (gerado pela fábrica; revise e evolua)."""
from __future__ import annotations

from datetime import date, datetime  # noqa: F401
from decimal import Decimal  # noqa: F401

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text  # noqa: F401
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models import utcnow


class Protocolo(Base):
    __tablename__ = "protocolos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    assunto: Mapped[str] = mapped_column(String(200), index=True)
    interessado_id: Mapped[int] = mapped_column(ForeignKey("interessados.id"), index=True)
    canal: Mapped[str] = mapped_column(String(30))
    prioridade: Mapped[str] = mapped_column(String(30))
    prazo: Mapped[date | None] = mapped_column(Date, nullable=True)
    valor_taxa: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    quantidade_folhas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sigiloso: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
