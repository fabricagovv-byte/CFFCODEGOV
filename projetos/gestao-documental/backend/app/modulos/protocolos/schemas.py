"""MOD-102 — Protocolos: esquemas de entrada e saída (validação)."""
from __future__ import annotations

from datetime import date, datetime  # noqa: F401
from decimal import Decimal  # noqa: F401
from typing import Literal  # noqa: F401

from pydantic import BaseModel, ConfigDict, Field, field_validator  # noqa: F401

from app.modulos.validadores import validar_cpf_cnpj  # noqa: F401


class ProtocoloIn(BaseModel):
    numero: str = Field(min_length=1, max_length=30)
    assunto: str = Field(min_length=1, max_length=200)
    interessado_id: int = Field(gt=0)
    canal: Literal['PRESENCIAL', 'EMAIL', 'PORTAL', 'TELEFONE']
    prioridade: Literal['NORMAL', 'URGENTE']
    prazo: date | None = Field(default=None)
    valor_taxa: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    quantidade_folhas: int | None = Field(default=None, ge=0, le=10000)
    sigiloso: bool | None = Field(default=None)

    @field_validator('numero', 'assunto')
    @classmethod
    def _sem_espacos(cls, v):
        if v is None:
            return v
        v = v.strip()
        return v

    @field_validator('numero', 'assunto')
    @classmethod
    def _obrigatorio(cls, v):
        if not v:
            raise ValueError("campo obrigatório")
        return v


class ProtocoloUpdate(BaseModel):
    numero: str | None = Field(default=None, max_length=30)
    assunto: str | None = Field(default=None, max_length=200)
    interessado_id: int | None = Field(default=None, gt=0)
    canal: Literal['PRESENCIAL', 'EMAIL', 'PORTAL', 'TELEFONE'] | None = Field(default=None)
    prioridade: Literal['NORMAL', 'URGENTE'] | None = Field(default=None)
    prazo: date | None = Field(default=None)
    valor_taxa: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    quantidade_folhas: int | None = Field(default=None, ge=0, le=10000)
    sigiloso: bool | None = Field(default=None)

    @field_validator('numero', 'assunto')
    @classmethod
    def _sem_espacos(cls, v):
        if v is None:
            return v
        v = v.strip()
        return v

    @field_validator('numero', 'assunto')
    @classmethod
    def _nao_vazio(cls, v):
        if v is not None and not v:
            raise ValueError("campo obrigatório")
        return v


class ProtocoloOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    numero: str
    assunto: str
    interessado_id: int
    canal: str
    prioridade: str
    prazo: date | None
    valor_taxa: Decimal | None
    quantidade_folhas: int | None
    sigiloso: bool | None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime


class PaginaProtocolo(BaseModel):
    total: int
    pagina: int
    por_pagina: int
    itens: list[ProtocoloOut]
