"""MOD-101 — Unidades: esquemas de entrada e saída (validação)."""
from __future__ import annotations

from datetime import date, datetime  # noqa: F401
from decimal import Decimal  # noqa: F401
from typing import Literal  # noqa: F401

from pydantic import BaseModel, ConfigDict, Field, field_validator  # noqa: F401

from app.modulos.validadores import validar_cpf_cnpj  # noqa: F401


class UnidadeIn(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    sigla: str = Field(min_length=1, max_length=20)
    municipio: str = Field(min_length=1, max_length=100)
    telefone: str | None = Field(default=None, max_length=20)

    @field_validator('nome', 'sigla', 'municipio', 'telefone')
    @classmethod
    def _sem_espacos(cls, v):
        if v is None:
            return v
        v = v.strip()
        return v

    @field_validator('nome', 'sigla', 'municipio')
    @classmethod
    def _obrigatorio(cls, v):
        if not v:
            raise ValueError("campo obrigatório")
        return v


class UnidadeUpdate(BaseModel):
    nome: str | None = Field(default=None, max_length=150)
    sigla: str | None = Field(default=None, max_length=20)
    municipio: str | None = Field(default=None, max_length=100)
    telefone: str | None = Field(default=None, max_length=20)

    @field_validator('nome', 'sigla', 'municipio', 'telefone')
    @classmethod
    def _sem_espacos(cls, v):
        if v is None:
            return v
        v = v.strip()
        return v

    @field_validator('nome', 'sigla', 'municipio')
    @classmethod
    def _nao_vazio(cls, v):
        if v is not None and not v:
            raise ValueError("campo obrigatório")
        return v


class UnidadeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    sigla: str
    municipio: str
    telefone: str | None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime


class PaginaUnidade(BaseModel):
    total: int
    pagina: int
    por_pagina: int
    itens: list[UnidadeOut]
