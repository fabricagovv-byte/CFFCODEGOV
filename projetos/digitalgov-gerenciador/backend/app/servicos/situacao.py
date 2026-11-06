"""Situação real de cada projeto: banco próprio, serviço no ar e código no repositório."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from .. import config
from ..modelos import Projeto


def cliente_http() -> httpx.Client:
    """Ponto único para as chamadas HTTP aos projetos (os testes trocam o transporte)."""
    return httpx.Client(timeout=5)


def banco(projeto: Projeto) -> dict[str, Any]:
    """Conecta no banco do projeto pela variável de ambiente indicada. A senha nunca aparece na resposta."""
    if not projeto.variavel_banco:
        return {"situacao": "NAO_CONFIGURADO", "mensagem": "Informe a variável de ambiente do banco do projeto"}
    url = os.getenv(projeto.variavel_banco)
    if not url:
        return {"situacao": "NAO_CONFIGURADO", "mensagem": f"A variável {projeto.variavel_banco} não está definida no servidor"}
    motor = create_engine(url, pool_pre_ping=True)
    try:
        with motor.connect() as c:
            nome = c.execute(text("SELECT current_database()")).scalar() if motor.dialect.name == "postgresql" else motor.url.database
            try:
                versao = c.execute(text("SELECT version_num FROM alembic_version")).scalar()
            except SQLAlchemyError:
                versao = None
        return {"situacao": "OK", "banco": nome, "migracao": versao,
                "mensagem": f"Conectado ao banco {nome}" + (f", migração {versao}" if versao else ", sem migrações aplicadas")}
    except SQLAlchemyError as erro:
        motivo = type(getattr(erro, "orig", erro)).__name__
        return {"situacao": "ERRO", "mensagem": f"Não conectou ao banco ({motivo}). Confira servidor, usuário e senha"}
    finally:
        motor.dispose()


def servico(projeto: Projeto) -> dict[str, Any]:
    if not projeto.url_servico:
        return {"situacao": "NAO_CONFIGURADO", "mensagem": "Informe o endereço do serviço do projeto"}
    try:
        with cliente_http() as c:
            r = c.get(projeto.url_servico.rstrip("/") + "/health")
        if r.status_code == 200:
            return {"situacao": "OK", "mensagem": "Serviço respondendo", "detalhe": r.json()}
        return {"situacao": "ERRO", "mensagem": f"Serviço respondeu {r.status_code}"}
    except httpx.HTTPError as erro:
        return {"situacao": "ERRO", "mensagem": f"Serviço não respondeu ({type(erro).__name__})"}


def codigo(projeto: Projeto) -> dict[str, Any]:
    """Último commit da pasta do projeto, se ela estiver num repositório git neste servidor."""
    if not projeto.pasta:
        return {"situacao": "NAO_CONFIGURADO", "mensagem": "Informe a pasta do projeto", "repositorio_url": projeto.repositorio_url}
    base = config.carregar().pasta_projetos.resolve()
    pasta = (base / projeto.pasta).resolve()
    if base not in pasta.parents and pasta != base or not pasta.is_dir():
        return {"situacao": "ERRO", "mensagem": "Pasta do projeto não encontrada", "repositorio_url": projeto.repositorio_url}
    r = subprocess.run(["git", "log", "-1", "--format=%h%x1f%cI%x1f%s", "--", "."], cwd=pasta, capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return {"situacao": "SEM_HISTORICO", "mensagem": "Pasta sem histórico no git", "repositorio_url": projeto.repositorio_url}
    sha, quando, assunto = r.stdout.strip().split("\x1f")
    return {"situacao": "OK", "ultimo_commit": sha, "data": quando, "mensagem": assunto, "repositorio_url": projeto.repositorio_url}


def completa(projeto: Projeto) -> dict[str, Any]:
    return {"banco": banco(projeto), "servico": servico(projeto), "codigo": codigo(projeto)}
