"""MOD-101 — Interessados: modelo de dados (gerado pela fábrica; revise e evolua)."""
from __future__ import annotations

from datetime import date, datetime  # noqa: F401
from decimal import Decimal  # noqa: F401

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text  # noqa: F401
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models import utcnow


class Interessado(Base):
    __tablename__ = "interessados"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), index=True)
    documento: Mapped[str] = mapped_column(String(14), unique=True, index=True)  # dado pessoal (LGPD)
    tipo_pessoa: Mapped[str] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)  # dado pessoal (LGPD)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)  # dado pessoal (LGPD)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
