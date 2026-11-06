from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Perfil = Literal["ADMIN", "GESTOR", "OPERADOR", "CONSULTA"]
Classificacao = Literal["PUBLICO", "RESTRITO", "SIGILOSO"]
StatusDoc = Literal["RASCUNHO", "ATIVO", "ARQUIVADO"]


class LoginIn(BaseModel):
    email: str = Field(max_length=254)
    senha: str = Field(min_length=1, max_length=200)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_em: datetime
    usuario: "UsuarioOut"


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    email: str
    perfil: Perfil
    ativo: bool


class UsuarioIn(BaseModel):
    nome: str = Field(min_length=3, max_length=150)
    email: str = Field(max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    senha: str = Field(min_length=10, max_length=72)
    perfil: Perfil = "CONSULTA"


class UsuarioUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=3, max_length=150)
    perfil: Perfil | None = None
    ativo: bool | None = None


class RecuperarIn(BaseModel):
    email: str = Field(max_length=254)


class RedefinirIn(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    nova_senha: str = Field(min_length=1, max_length=200)


class ArquivoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome_original: str
    tamanho: int
    sha256: str
    enviado_em: datetime


class DocumentoIn(BaseModel):
    titulo: str = Field(min_length=3, max_length=300)
    tipo: str = Field(min_length=2, max_length=60)
    assunto: str = Field(default="", max_length=5000)
    interessado: str = Field(default="", max_length=200)
    classificacao: Classificacao = "PUBLICO"
    status: StatusDoc = "ATIVO"

    @field_validator("titulo", "tipo")
    @classmethod
    def _sem_espacos(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("campo obrigatório")
        return v


class DocumentoUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=300)
    tipo: str | None = Field(default=None, min_length=2, max_length=60)
    assunto: str | None = Field(default=None, max_length=5000)
    interessado: str | None = Field(default=None, max_length=200)
    classificacao: Classificacao | None = None
    status: StatusDoc | None = None

    @field_validator("titulo", "tipo")
    @classmethod
    def _sem_espacos(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) < 2:
            raise ValueError("campo obrigatório")
        return v.strip() if v else v


class DocumentoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    numero: str
    titulo: str
    tipo: str
    assunto: str
    interessado: str
    classificacao: Classificacao
    status: StatusDoc
    criado_em: datetime
    atualizado_em: datetime
    arquivos: list[ArquivoOut] = []


class Pagina(BaseModel):
    total: int
    pagina: int
    por_pagina: int
    itens: list


class PaginaDocumentos(Pagina):
    itens: list[DocumentoOut]


class AuditoriaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    momento: datetime
    usuario_id: int | None
    acao: str
    recurso: str
    recurso_id: str
    ip: str
    detalhes: str


class PaginaAuditoria(Pagina):
    itens: list[AuditoriaOut]


TokenOut.model_rebuild()
