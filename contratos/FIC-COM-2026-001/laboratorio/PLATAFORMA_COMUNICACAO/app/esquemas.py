"""Dados de entrada da API, com validação."""
from __future__ import annotations

import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

Perfil = Literal["ADMIN", "EDITOR", "APPROVER", "VIEWER"]
Prioridade = Literal["BAIXA", "NORMAL", "ALTA"]
EstadoChamado = Literal["ABERTO", "EM_ATENDIMENTO", "RESOLVIDO"]

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Login(BaseModel):
    username: str
    password: str


class UsuarioNovo(BaseModel):
    name: str = Field(min_length=2)
    username: str = Field(min_length=3)
    password: str = Field(min_length=12)
    role: Perfil


class CanalNovo(BaseModel):
    name: str = Field(min_length=2)
    description: str = ""
    is_public: bool = False


class PublicacaoNova(BaseModel):
    channel_id: int
    title: str = Field(min_length=4)
    body: str = Field(min_length=8)


class CampanhaNova(BaseModel):
    name: str = Field(min_length=3)
    objective: str = Field(min_length=4)
    channel_id: Optional[int] = None
    starts_on: Optional[str] = None
    ends_on: Optional[str] = None


class ContatoNovo(BaseModel):
    name: str = Field(min_length=2)
    email: Optional[str] = None
    category: str = "PUBLICO"
    consent: bool = False

    @field_validator("email")
    @classmethod
    def email_valido(cls, valor: Optional[str]) -> Optional[str]:
        if valor in (None, ""):
            return None
        valor = valor.strip()
        if len(valor) > 254 or not _EMAIL.match(valor):
            raise ValueError("E-mail inválido")
        return valor


class ChamadoNovo(BaseModel):
    subject: str = Field(min_length=5)
    description: str = Field(min_length=8)
    priority: Prioridade = "NORMAL"
    contact_id: Optional[int] = None


class EstadoDoChamado(BaseModel):
    status: EstadoChamado
