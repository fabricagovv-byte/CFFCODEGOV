"""Tabelas do banco central. Dados administrativos apenas: nenhum dado de negócio dos projetos fica aqui."""
from __future__ import annotations

from datetime import date, datetime, time, timezone
from decimal import Decimal

from sqlalchemy import (Boolean, CheckConstraint, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Time,
                        UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def agora() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    login: Mapped[str] = mapped_column(String(60), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[str] = mapped_column(String(20))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    __table_args__ = (CheckConstraint("perfil IN ('ADMIN','GESTOR','CONSULTA')", name="ck_usuarios_perfil"),)


class Sessao(Base):
    __tablename__ = "sessoes"
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    encerrada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class TentativaLogin(Base):
    __tablename__ = "tentativas_login"
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(60), index=True)
    sucesso: Mapped[bool] = mapped_column(Boolean)
    em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, index=True)


class Orgao(Base):
    __tablename__ = "orgaos"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200))
    sigla: Mapped[str | None] = mapped_column(String(30))
    cnpj: Mapped[str | None] = mapped_column(String(18))
    esfera: Mapped[str | None] = mapped_column(String(20))
    contato: Mapped[str | None] = mapped_column(String(200))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)


class Contrato(Base):
    __tablename__ = "contratos"
    id: Mapped[int] = mapped_column(primary_key=True)
    orgao_id: Mapped[int] = mapped_column(ForeignKey("orgaos.id"), index=True)
    numero: Mapped[str] = mapped_column(String(60), unique=True)
    objeto: Mapped[str] = mapped_column(Text)
    metrica: Mapped[str] = mapped_column(String(10))
    unidade_outra: Mapped[str | None] = mapped_column(String(40))
    quantidade_contratada: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    valor_unitario: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    vigencia_inicio: Mapped[date | None] = mapped_column(Date)
    vigencia_fim: Mapped[date | None] = mapped_column(Date)
    situacao: Mapped[str] = mapped_column(String(20), default="ATIVO")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    __table_args__ = (
        CheckConstraint("metrica IN ('UST','HST','PF','OUTRA')", name="ck_contratos_metrica"),
        CheckConstraint("situacao IN ('ATIVO','SUSPENSO','ENCERRADO')", name="ck_contratos_situacao"),
    )


class Documento(Base):
    __tablename__ = "documentos"
    id: Mapped[int] = mapped_column(primary_key=True)
    contrato_id: Mapped[int | None] = mapped_column(ForeignKey("contratos.id"), index=True)
    projeto_id: Mapped[int | None] = mapped_column(ForeignKey("projetos.id"), index=True)
    tipo: Mapped[str] = mapped_column(String(20))
    titulo: Mapped[str] = mapped_column(String(200))
    nome_arquivo: Mapped[str] = mapped_column(String(255))
    caminho: Mapped[str] = mapped_column(String(500))
    tamanho: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64))
    enviado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    enviado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    __table_args__ = (CheckConstraint("tipo IN ('EDITAL','TR','CONTRATO','OS','TERMO_ACEITE','RELATORIO','OUTRO')",
                                      name="ck_documentos_tipo"),)


class OrdemServico(Base):
    __tablename__ = "ordens_servico"
    id: Mapped[int] = mapped_column(primary_key=True)
    contrato_id: Mapped[int] = mapped_column(ForeignKey("contratos.id"), index=True)
    numero: Mapped[str] = mapped_column(String(60))
    descricao: Mapped[str] = mapped_column(Text)
    quantidade: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    autorizada: Mapped[bool] = mapped_column(Boolean, default=False)
    autorizado_por: Mapped[str | None] = mapped_column(String(200))
    autorizado_em: Mapped[date | None] = mapped_column(Date)
    documento_id: Mapped[int | None] = mapped_column(ForeignKey("documentos.id", use_alter=True, name="fk_os_documento"))
    __table_args__ = (UniqueConstraint("contrato_id", "numero", name="uq_os_contrato_numero"),)


class Projeto(Base):
    __tablename__ = "projetos"
    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(60), unique=True)
    nome: Mapped[str] = mapped_column(String(200))
    contrato_id: Mapped[int | None] = mapped_column(ForeignKey("contratos.id"), index=True)
    os_id: Mapped[int | None] = mapped_column(ForeignKey("ordens_servico.id"))
    descricao: Mapped[str | None] = mapped_column(Text)
    pasta: Mapped[str | None] = mapped_column(String(300))
    repositorio_url: Mapped[str | None] = mapped_column(String(300))
    url_servico: Mapped[str | None] = mapped_column(String(300))
    variavel_banco: Mapped[str | None] = mapped_column(String(80))
    variavel_token: Mapped[str | None] = mapped_column(String(80))
    integracao_agentes: Mapped[str] = mapped_column(String(20), default="PENDENTE")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)


class Profissional(Base):
    __tablename__ = "profissionais"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200))
    cargo: Mapped[str] = mapped_column(String(120))
    perfil: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(200))
    cpf_mascarado: Mapped[str | None] = mapped_column(String(14))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)


class Agente(Base):
    __tablename__ = "agentes"
    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nome: Mapped[str] = mapped_column(String(120))
    funcao: Mapped[str | None] = mapped_column(Text)
    projeto_id: Mapped[int | None] = mapped_column(ForeignKey("projetos.id"))
    profissional_id: Mapped[int | None] = mapped_column(ForeignKey("profissionais.id"))
    situacao: Mapped[str] = mapped_column(String(25), default="INTEGRACAO_PENDENTE")
    __table_args__ = (CheckConstraint("situacao IN ('INTEGRACAO_PENDENTE','CONFIGURADO','ATIVO','INATIVO')",
                                      name="ck_agentes_situacao"),)


class Tarefa(Base):
    __tablename__ = "tarefas"
    id: Mapped[int] = mapped_column(primary_key=True)
    projeto_id: Mapped[int] = mapped_column(ForeignKey("projetos.id"), index=True)
    titulo: Mapped[str] = mapped_column(String(200))
    descricao: Mapped[str | None] = mapped_column(Text)
    situacao: Mapped[str] = mapped_column(String(20), default="A_FAZER")
    profissional_id: Mapped[int | None] = mapped_column(ForeignKey("profissionais.id"))
    agente_id: Mapped[int | None] = mapped_column(ForeignKey("agentes.id"))
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    concluida_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (CheckConstraint("situacao IN ('A_FAZER','EM_ANDAMENTO','EM_REVISAO','CONCLUIDA','BLOQUEADA')",
                                      name="ck_tarefas_situacao"),)


class Evidencia(Base):
    __tablename__ = "evidencias"
    id: Mapped[int] = mapped_column(primary_key=True)
    projeto_id: Mapped[int] = mapped_column(ForeignKey("projetos.id"), index=True)
    tarefa_id: Mapped[int | None] = mapped_column(ForeignKey("tarefas.id"))
    tipo: Mapped[str] = mapped_column(String(20))
    descricao: Mapped[str] = mapped_column(Text)
    referencia: Mapped[str | None] = mapped_column(String(300))
    documento_id: Mapped[int | None] = mapped_column(ForeignKey("documentos.id"))
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    __table_args__ = (CheckConstraint("tipo IN ('COMMIT','TESTE','CAPTURA','LOG','DOCUMENTO','OUTRO')",
                                      name="ck_evidencias_tipo"),)


class ExecucaoTeste(Base):
    __tablename__ = "execucoes_teste"
    id: Mapped[int] = mapped_column(primary_key=True)
    projeto_id: Mapped[int] = mapped_column(ForeignKey("projetos.id"), index=True)
    origem: Mapped[str] = mapped_column(String(200))
    total: Mapped[int] = mapped_column(Integer)
    falhas: Mapped[int] = mapped_column(Integer)
    erros: Mapped[int] = mapped_column(Integer)
    ignorados: Mapped[int] = mapped_column(Integer)
    executado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    documento_id: Mapped[int | None] = mapped_column(ForeignKey("documentos.id"))


class LancamentoHoras(Base):
    """Horas preenchidas manualmente. O sistema nunca altera um lançamento por conta própria."""
    __tablename__ = "lancamentos_horas"
    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(String(10))
    profissional_id: Mapped[int | None] = mapped_column(ForeignKey("profissionais.id"), index=True)
    agente_id: Mapped[int | None] = mapped_column(ForeignKey("agentes.id"))
    projeto_id: Mapped[int | None] = mapped_column(ForeignKey("projetos.id"), index=True)
    contrato_id: Mapped[int | None] = mapped_column(ForeignKey("contratos.id"), index=True)
    data: Mapped[date] = mapped_column(Date, index=True)
    inicio: Mapped[time] = mapped_column(Time)
    fim: Mapped[time] = mapped_column(Time)
    intervalo_min: Mapped[int] = mapped_column(Integer, default=0)
    atividade: Mapped[str] = mapped_column(Text)
    evidencia: Mapped[str | None] = mapped_column(String(300))
    lancado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    lancado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    __table_args__ = (
        CheckConstraint("tipo IN ('HUMANA','IA')", name="ck_horas_tipo"),
        CheckConstraint("fim > inicio", name="ck_horas_periodo"),
        CheckConstraint("intervalo_min >= 0", name="ck_horas_intervalo"),
        CheckConstraint("(tipo = 'HUMANA' AND profissional_id IS NOT NULL) OR (tipo = 'IA' AND agente_id IS NOT NULL)",
                        name="ck_horas_responsavel"),
    )


class AceiteHoras(Base):
    """Horas humanas aceitas para faturamento, registradas à parte do lançamento."""
    __tablename__ = "aceites_horas"
    id: Mapped[int] = mapped_column(primary_key=True)
    lancamento_id: Mapped[int] = mapped_column(ForeignKey("lancamentos_horas.id", ondelete="CASCADE"), unique=True)
    aceito_por: Mapped[str] = mapped_column(String(200))
    documento: Mapped[str] = mapped_column(String(300))
    aceito_em: Mapped[date] = mapped_column(Date)
    registrado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))


class Medicao(Base):
    __tablename__ = "medicoes"
    id: Mapped[int] = mapped_column(primary_key=True)
    contrato_id: Mapped[int] = mapped_column(ForeignKey("contratos.id"), index=True)
    os_id: Mapped[int | None] = mapped_column(ForeignKey("ordens_servico.id"))
    projeto_id: Mapped[int | None] = mapped_column(ForeignKey("projetos.id"))
    item: Mapped[str] = mapped_column(String(80))
    descricao: Mapped[str] = mapped_column(Text)
    quantidade: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    data_execucao: Mapped[date] = mapped_column(Date)
    situacao: Mapped[str] = mapped_column(String(15), default="EXECUTADA")
    documento_aceite: Mapped[str | None] = mapped_column(String(300))
    observacao: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (
        CheckConstraint("situacao IN ('EXECUTADA','ACEITA','GLOSADA','PAGA')", name="ck_medicoes_situacao"),
        CheckConstraint("quantidade >= 0", name="ck_medicoes_quantidade"),
    )


class ExecucaoStart(Base):
    __tablename__ = "execucoes_start"
    id: Mapped[int] = mapped_column(primary_key=True)
    projeto_id: Mapped[int] = mapped_column(ForeignKey("projetos.id"), index=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    resultado: Mapped[str] = mapped_column(String(25))
    etapas: Mapped[str] = mapped_column(Text)


class Auditoria(Base):
    __tablename__ = "auditoria"
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    acao: Mapped[str] = mapped_column(String(40))
    entidade: Mapped[str] = mapped_column(String(40))
    entidade_id: Mapped[int | None] = mapped_column(Integer)
    em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, index=True)
    detalhe: Mapped[str] = mapped_column(Text, default="{}")
