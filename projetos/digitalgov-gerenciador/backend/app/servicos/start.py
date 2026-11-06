"""START de um projeto: confere as autorizações e inicia só o que está realmente configurado."""
from __future__ import annotations

import os
from datetime import date
from typing import Any

import httpx
from sqlalchemy.orm import Session

from ..modelos import Contrato, OrdemServico, Projeto
from . import situacao


def _etapa(nome: str, ok: bool | None, mensagem: str) -> dict[str, Any]:
    return {"etapa": nome, "situacao": "OK" if ok else ("PENDENTE" if ok is None else "BLOQUEADO"), "mensagem": mensagem}


def executar(s: Session, projeto: Projeto, hoje: date | None = None) -> dict[str, Any]:
    hoje = hoje or date.today()
    etapas: list[dict[str, Any]] = [_etapa("Projeto ativo", projeto.ativo, "Ativo" if projeto.ativo else "Projeto desativado")]

    contrato = s.get(Contrato, projeto.contrato_id) if projeto.contrato_id else None
    if not contrato:
        etapas.append(_etapa("Contrato vigente", False, "Projeto sem contrato vinculado"))
    else:
        vigente = contrato.situacao == "ATIVO" and (not contrato.vigencia_inicio or contrato.vigencia_inicio <= hoje) \
            and (not contrato.vigencia_fim or hoje <= contrato.vigencia_fim)
        etapas.append(_etapa("Contrato vigente", vigente, f"Contrato {contrato.numero}: " + ("vigente" if vigente else "fora da vigência ou não ativo")))

    os_ = s.get(OrdemServico, projeto.os_id) if projeto.os_id else None
    if not os_:
        etapas.append(_etapa("Ordem de serviço autorizada", False, "Projeto sem ordem de serviço vinculada"))
    else:
        etapas.append(_etapa("Ordem de serviço autorizada", os_.autorizada,
                             f"OS {os_.numero} autorizada por {os_.autorizado_por} em {os_.autorizado_em:%d/%m/%Y}"
                             if os_.autorizada else f"OS {os_.numero} sem autorização registrada"))

    autorizado = all(e["situacao"] == "OK" for e in etapas)
    banco = situacao.banco(projeto)
    etapas.append(_etapa("Banco de dados do projeto", banco["situacao"] == "OK", banco["mensagem"]))
    serv = situacao.servico(projeto)
    etapas.append(_etapa("Serviço do projeto", serv["situacao"] == "OK", serv["mensagem"]))

    resultado = "BLOQUEADO"
    if not autorizado:
        etapas.append(_etapa("Início da produção", False, "Não iniciado: faltam autorizações"))
    elif banco["situacao"] != "OK" or serv["situacao"] != "OK":
        etapas.append(_etapa("Início da produção", False, "Não iniciado: banco ou serviço do projeto não está pronto"))
    else:
        token = os.getenv(projeto.variavel_token) if projeto.variavel_token else None
        try:
            with situacao.cliente_http() as c:
                r = c.post(projeto.url_servico.rstrip("/") + "/api/gerenciador/start",
                           headers={"Authorization": f"Bearer {token}"} if token else {})
            if r.status_code == 200:
                resultado = "INICIADO"
                etapas.append(_etapa("Início da produção", True, r.json().get("mensagem", "Serviço iniciou o ciclo de produção")))
            else:
                etapas.append(_etapa("Início da produção", False, f"O serviço recusou o início (HTTP {r.status_code})"))
        except httpx.HTTPError as erro:
            etapas.append(_etapa("Início da produção", False, f"O serviço não respondeu ({type(erro).__name__})"))

    if projeto.integracao_agentes != "CONFIGURADA":
        etapas.append(_etapa("Agentes (Codex)", None, "Integração pendente"))
        if resultado == "INICIADO":
            resultado = "INICIADO_SEM_AGENTES"
    else:
        etapas.append(_etapa("Agentes (Codex)", None, "Integração pendente: o conector com o executor ainda não foi instalado"))
    return {"resultado": resultado, "etapas": etapas}
