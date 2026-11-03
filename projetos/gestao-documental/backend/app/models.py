"""Modelo de dados. Mantenha em sincronia com migrations/versions (alembic check)."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


PERFIS = ("ADMIN", "GESTOR", "OPERADOR", "CONSULTA")
CLASSIFICACOES = ("PUBLICO", "RESTRITO", "SIGILOSO")  # LAI: acesso público x restrito
STATUS_DOC = ("RASCUNHO", "ATIVO", "ARQUIVADO")


class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(100))
    perfil: Mapped[str] = mapped_column(String(20), default="CONSULTA")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    versao_sessao: Mapped[int] = mapped_column(Integer, default=0, server_default="0")  # muda ao trocar senha
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class TokenRecuperacao(Base):
    __tablename__ = "tokens_recuperacao"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    usado: Mapped[bool] = mapped_column(Boolean, default=False)


class TokenRevogado(Base):
    __tablename__ = "tokens_revogados"
    jti: Mapped[str] = mapped_column(String(64), primary_key=True)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class Documento(Base):
    __tablename__ = "documentos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    titulo: Mapped[str] = mapped_column(String(300))
    tipo: Mapped[str] = mapped_column(String(60), index=True)
    assunto: Mapped[str] = mapped_column(Text, default="")
    interessado: Mapped[str] = mapped_column(String(200), default="")  # pode conter dado pessoal
    classificacao: Mapped[str] = mapped_column(String(20), default="PUBLICO", index=True)
    status: Mapped[str] = mapped_column(String(20), default="ATIVO", index=True)
    criado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    arquivos: Mapped[list["Arquivo"]] = relationship(back_populates="documento", order_by="Arquivo.id")


class Arquivo(Base):
    __tablename__ = "arquivos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    documento_id: Mapped[int] = mapped_column(ForeignKey("documentos.id", ondelete="CASCADE"), index=True)
    nome_original: Mapped[str] = mapped_column(String(255))
    caminho: Mapped[str] = mapped_column(String(500))
    tamanho: Mapped[int] = mapped_column(BigInteger)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    enviado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    enviado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    documento: Mapped[Documento] = relationship(back_populates="arquivos")


class RegistroAuditoria(Base):
    """Trilha de auditoria. Somente inserção (trigger no PostgreSQL impede UPDATE/DELETE)."""
    __tablename__ = "auditoria"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    momento: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True, index=True)
    acao: Mapped[str] = mapped_column(String(60), index=True)
    recurso: Mapped[str] = mapped_column(String(60))
    recurso_id: Mapped[str] = mapped_column(String(60), default="")
    ip: Mapped[str] = mapped_column(String(45), default="")
    detalhes: Mapped[str] = mapped_column(Text, default="")


Index("ix_auditoria_recurso", RegistroAuditoria.recurso, RegistroAuditoria.recurso_id)
