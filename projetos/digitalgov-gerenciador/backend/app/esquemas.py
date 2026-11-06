"""Validação dos dados que entram pela API."""
from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_URL = r"^https?://[^\s]+$"


class Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class UsuarioNovo(Base):
    nome: str = Field(min_length=2, max_length=120)
    login: str = Field(min_length=3, max_length=60, pattern=r"^[a-z0-9._-]+$")
    senha: str = Field(min_length=12, max_length=200)
    perfil: Literal["ADMIN", "GESTOR", "CONSULTA"]


class OrgaoNovo(Base):
    nome: str = Field(min_length=2, max_length=200)
    sigla: Optional[str] = Field(None, max_length=30)
    cnpj: Optional[str] = Field(None, pattern=r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$")
    esfera: Optional[Literal["FEDERAL", "ESTADUAL", "MUNICIPAL", "DISTRITAL"]] = None
    contato: Optional[str] = Field(None, max_length=200)


class ContratoNovo(Base):
    orgao_id: int
    numero: str = Field(min_length=1, max_length=60)
    objeto: str = Field(min_length=3)
    metrica: Literal["UST", "HST", "PF", "OUTRA"]
    unidade_outra: Optional[str] = Field(None, max_length=40)
    quantidade_contratada: Optional[Decimal] = Field(None, ge=0)
    valor_unitario: Optional[Decimal] = Field(None, ge=0)
    vigencia_inicio: Optional[date] = None
    vigencia_fim: Optional[date] = None
    situacao: Literal["ATIVO", "SUSPENSO", "ENCERRADO"] = "ATIVO"

    @model_validator(mode="after")
    def conferir(self) -> "ContratoNovo":
        if self.vigencia_inicio and self.vigencia_fim and self.vigencia_fim < self.vigencia_inicio:
            raise ValueError("O fim da vigência é anterior ao início")
        if self.metrica == "OUTRA" and not self.unidade_outra:
            raise ValueError("Informe a unidade quando a métrica for OUTRA")
        return self


class OrdemServicoNova(Base):
    contrato_id: int
    numero: str = Field(min_length=1, max_length=60)
    descricao: str = Field(min_length=3)
    quantidade: Optional[Decimal] = Field(None, ge=0)
    autorizada: bool = False
    autorizado_por: Optional[str] = Field(None, max_length=200)
    autorizado_em: Optional[date] = None
    documento_id: Optional[int] = None

    @model_validator(mode="after")
    def conferir(self) -> "OrdemServicoNova":
        if self.autorizada and not (self.autorizado_por and self.autorizado_em):
            raise ValueError("OS autorizada precisa de quem autorizou e da data")
        return self


class ProjetoNovo(Base):
    codigo: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,59}$")
    nome: str = Field(min_length=2, max_length=200)
    contrato_id: Optional[int] = None
    os_id: Optional[int] = None
    descricao: Optional[str] = None
    pasta: Optional[str] = Field(None, max_length=300)
    repositorio_url: Optional[str] = Field(None, pattern=_URL)
    url_servico: Optional[str] = Field(None, pattern=_URL)
    variavel_banco: Optional[str] = Field(None, pattern=r"^[A-Z][A-Z0-9_]{2,79}$")
    variavel_token: Optional[str] = Field(None, pattern=r"^[A-Z][A-Z0-9_]{2,79}$")
    integracao_agentes: Literal["PENDENTE", "CONFIGURADA"] = "PENDENTE"
    ativo: bool = True

    @field_validator("pasta")
    @classmethod
    def pasta_relativa(cls, v: Optional[str]) -> Optional[str]:
        if v and (v.startswith("/") or ".." in v.split("/")):
            raise ValueError("A pasta é relativa à pasta de projetos e não pode subir de nível")
        return v


class ProfissionalNovo(Base):
    nome: str = Field(min_length=2, max_length=200)
    cargo: str = Field(min_length=2, max_length=120)
    perfil: Optional[str] = Field(None, max_length=120)
    email: Optional[str] = Field(None, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    cpf_mascarado: Optional[str] = Field(None, pattern=r"^\*{3}\.\d{3}\.\d{3}-\*{2}$",
                                         description="Somente mascarado, ex.: ***.456.789-**")
    ativo: bool = True


class AgenteNovo(Base):
    codigo: str = Field(min_length=2, max_length=20)
    nome: str = Field(min_length=2, max_length=120)
    funcao: Optional[str] = None
    projeto_id: Optional[int] = None
    profissional_id: Optional[int] = None
    situacao: Literal["INTEGRACAO_PENDENTE", "CONFIGURADO", "ATIVO", "INATIVO"] = "INTEGRACAO_PENDENTE"


class TarefaNova(Base):
    projeto_id: int
    titulo: str = Field(min_length=3, max_length=200)
    descricao: Optional[str] = None
    situacao: Literal["A_FAZER", "EM_ANDAMENTO", "EM_REVISAO", "CONCLUIDA", "BLOQUEADA"] = "A_FAZER"
    profissional_id: Optional[int] = None
    agente_id: Optional[int] = None


class EvidenciaNova(Base):
    projeto_id: int
    tarefa_id: Optional[int] = None
    tipo: Literal["COMMIT", "TESTE", "CAPTURA", "LOG", "DOCUMENTO", "OUTRO"]
    descricao: str = Field(min_length=3)
    referencia: Optional[str] = Field(None, max_length=300)
    documento_id: Optional[int] = None


class MedicaoNova(Base):
    contrato_id: int
    os_id: Optional[int] = None
    projeto_id: Optional[int] = None
    item: str = Field(min_length=1, max_length=80)
    descricao: str = Field(min_length=3)
    quantidade: Decimal = Field(ge=0)
    data_execucao: date
    situacao: Literal["EXECUTADA", "ACEITA", "GLOSADA", "PAGA"] = "EXECUTADA"
    documento_aceite: Optional[str] = Field(None, max_length=300)
    observacao: Optional[str] = None

    @model_validator(mode="after")
    def conferir(self) -> "MedicaoNova":
        if self.situacao in ("ACEITA", "PAGA") and not self.documento_aceite:
            raise ValueError("Medição aceita ou paga precisa do documento de aceite do órgão")
        return self


class LancamentoNovo(Base):
    tipo: Literal["HUMANA", "IA"]
    profissional_id: Optional[int] = None
    agente_id: Optional[int] = None
    projeto_id: Optional[int] = None
    contrato_id: Optional[int] = None
    data: date
    inicio: time
    fim: time
    intervalo_min: int = Field(0, ge=0, le=600)
    atividade: str = Field(min_length=3)
    evidencia: Optional[str] = Field(None, max_length=300)

    @model_validator(mode="after")
    def conferir(self) -> "LancamentoNovo":
        if self.tipo == "HUMANA" and not self.profissional_id:
            raise ValueError("Hora humana precisa do profissional")
        if self.tipo == "IA" and not self.agente_id:
            raise ValueError("Hora de IA precisa do agente")
        if self.tipo == "IA" and self.profissional_id:
            raise ValueError("Hora de IA não é lançada em nome de profissional")
        if self.fim <= self.inicio:
            raise ValueError("O fim precisa ser depois do início (turno que passa da meia-noite: lance em dois dias)")
        minutos = (self.fim.hour * 60 + self.fim.minute) - (self.inicio.hour * 60 + self.inicio.minute)
        if self.intervalo_min >= minutos:
            raise ValueError("O intervalo é maior ou igual ao período trabalhado")
        return self


class AceiteNovo(Base):
    aceito_por: str = Field(min_length=3, max_length=200)
    documento: str = Field(min_length=3, max_length=300)
    aceito_em: date
