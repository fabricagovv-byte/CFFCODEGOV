"""MOD-101 — Interessados: esquemas de entrada e saída (validação)."""
from __future__ import annotations

from datetime import date, datetime  # noqa: F401
from decimal import Decimal  # noqa: F401
from typing import Literal  # noqa: F401

from pydantic import BaseModel, ConfigDict, Field, field_validator  # noqa: F401

from app.modulos.validadores import validar_cpf_cnpj  # noqa: F401


class InteressadoIn(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    documento: str
    tipo_pessoa: Literal['FISICA', 'JURIDICA']
    email: str | None = Field(default=None, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    telefone: str | None = Field(default=None, max_length=20)
    observacoes: str | None = Field(default=None, max_length=5000)

    @field_validator('nome', 'telefone', 'observacoes')
    @classmethod
    def _sem_espacos(cls, v):
        if v is None:
            return v
        v = v.strip()
        return v

    @field_validator('documento')
    @classmethod
    def _cpf_cnpj(cls, v):
        return v if v is None else validar_cpf_cnpj(v)

    @field_validator('nome')
    @classmethod
    def _obrigatorio(cls, v):
        if not v:
            raise ValueError("campo obrigatório")
        return v


class InteressadoUpdate(BaseModel):
    nome: str | None = Field(default=None, max_length=150)
    documento: str | None = Field(default=None)
    tipo_pessoa: Literal['FISICA', 'JURIDICA'] | None = Field(default=None)
    email: str | None = Field(default=None, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    telefone: str | None = Field(default=None, max_length=20)
    observacoes: str | None = Field(default=None, max_length=5000)

    @field_validator('nome', 'telefone', 'observacoes')
    @classmethod
    def _sem_espacos(cls, v):
        if v is None:
            return v
        v = v.strip()
        return v

    @field_validator('documento')
    @classmethod
    def _cpf_cnpj(cls, v):
        return v if v is None else validar_cpf_cnpj(v)

    @field_validator('nome')
    @classmethod
    def _nao_vazio(cls, v):
        if v is not None and not v:
            raise ValueError("campo obrigatório")
        return v


class InteressadoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    documento: str
    tipo_pessoa: str
    email: str | None
    telefone: str | None
    observacoes: str | None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime


class PaginaInteressado(BaseModel):
    total: int
    pagina: int
    por_pagina: int
    itens: list[InteressadoOut]
