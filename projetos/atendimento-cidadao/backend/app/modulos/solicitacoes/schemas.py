"""MOD-103 — Solicitações: esquemas de entrada e saída (validação)."""
from __future__ import annotations

from datetime import date, datetime  # noqa: F401
from decimal import Decimal  # noqa: F401
from typing import Literal  # noqa: F401

from pydantic import BaseModel, ConfigDict, Field, field_validator  # noqa: F401

from app.modulos.validadores import validar_cpf_cnpj  # noqa: F401


class SolicitacaoIn(BaseModel):
    protocolo: str = Field(min_length=1, max_length=30)
    cidadao_id: int = Field(gt=0)
    unidade_id: int = Field(gt=0)
    canal: Literal['PRESENCIAL', 'PORTAL', 'TELEFONE', 'WHATSAPP']
    assunto: str = Field(min_length=1, max_length=200)
    descricao: str | None = Field(default=None, max_length=5000)
    situacao: Literal['ABERTA', 'EM_ATENDIMENTO', 'CONCLUIDA', 'CANCELADA']
    prazo: date | None = Field(default=None)
    prioritaria: bool | None = Field(default=None)

    @field_validator('protocolo', 'assunto', 'descricao')
    @classmethod
    def _sem_espacos(cls, v):
        if v is None:
            return v
        v = v.strip()
        return v

    @field_validator('protocolo', 'assunto')
    @classmethod
    def _obrigatorio(cls, v):
        if not v:
            raise ValueError("campo obrigatório")
        return v


class SolicitacaoUpdate(BaseModel):
    protocolo: str | None = Field(default=None, max_length=30)
    cidadao_id: int | None = Field(default=None, gt=0)
    unidade_id: int | None = Field(default=None, gt=0)
    canal: Literal['PRESENCIAL', 'PORTAL', 'TELEFONE', 'WHATSAPP'] | None = Field(default=None)
    assunto: str | None = Field(default=None, max_length=200)
    descricao: str | None = Field(default=None, max_length=5000)
    situacao: Literal['ABERTA', 'EM_ATENDIMENTO', 'CONCLUIDA', 'CANCELADA'] | None = Field(default=None)
    prazo: date | None = Field(default=None)
    prioritaria: bool | None = Field(default=None)

    @field_validator('protocolo', 'assunto', 'descricao')
    @classmethod
    def _sem_espacos(cls, v):
        if v is None:
            return v
        v = v.strip()
        return v

    @field_validator('protocolo', 'assunto')
    @classmethod
    def _nao_vazio(cls, v):
        if v is not None and not v:
            raise ValueError("campo obrigatório")
        return v


class SolicitacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    protocolo: str
    cidadao_id: int
    unidade_id: int
    canal: str
    assunto: str
    descricao: str | None
    situacao: str
    prazo: date | None
    prioritaria: bool | None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime


class PaginaSolicitacao(BaseModel):
    total: int
    pagina: int
    por_pagina: int
    itens: list[SolicitacaoOut]
