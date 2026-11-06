"""MOD-101 — Unidades: modelo de dados (gerado pela fábrica; revise e evolua)."""
from __future__ import annotations

from datetime import date, datetime  # noqa: F401
from decimal import Decimal  # noqa: F401

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text  # noqa: F401
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models import utcnow


class Unidade(Base):
    __tablename__ = "unidades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), index=True)
    sigla: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    municipio: Mapped[str] = mapped_column(String(100))
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
