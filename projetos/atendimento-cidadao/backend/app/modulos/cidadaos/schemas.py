"""MOD-102 — Cidadãos: esquemas de entrada e saída (validação)."""
from __future__ import annotations

from datetime import date, datetime  # noqa: F401
from decimal import Decimal  # noqa: F401
from typing import Literal  # noqa: F401

from pydantic import BaseModel, ConfigDict, Field, field_validator  # noqa: F401

from app.modulos.validadores import validar_cpf_cnpj  # noqa: F401


class CidadaoIn(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    cpf: str
    email: str | None = Field(default=None, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    telefone: str | None = Field(default=None, max_length=20)
    data_nascimento: date | None = Field(default=None)

    @field_validator('nome', 'telefone')
    @classmethod
    def _sem_espacos(cls, v):
        if v is None:
            return v
        v = v.strip()
        return v

    @field_validator('cpf')
    @classmethod
    def _cpf_cnpj(cls, v):
        return v if v is None else validar_cpf_cnpj(v)

    @field_validator('nome')
    @classmethod
    def _obrigatorio(cls, v):
        if not v:
            raise ValueError("campo obrigatório")
        return v


class CidadaoUpdate(BaseModel):
    nome: str | None = Field(default=None, max_length=150)
    cpf: str | None = Field(default=None)
    email: str | None = Field(default=None, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    telefone: str | None = Field(default=None, max_length=20)
    data_nascimento: date | None = Field(default=None)

    @field_validator('nome', 'telefone')
    @classmethod
    def _sem_espacos(cls, v):
        if v is None:
            return v
        v = v.strip()
        return v

    @field_validator('cpf')
    @classmethod
    def _cpf_cnpj(cls, v):
        return v if v is None else validar_cpf_cnpj(v)

    @field_validator('nome')
    @classmethod
    def _nao_vazio(cls, v):
        if v is not None and not v:
            raise ValueError("campo obrigatório")
        return v


class CidadaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    cpf: str
    email: str | None
    telefone: str | None
    data_nascimento: date | None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime


class PaginaCidadao(BaseModel):
    total: int
    pagina: int
    por_pagina: int
    itens: list[CidadaoOut]
