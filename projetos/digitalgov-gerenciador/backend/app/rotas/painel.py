"""Visão geral e resumo das medições por contrato."""
from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..acesso import usuario_atual
from ..db import sessao
from ..modelos import Contrato, ExecucaoStart, Medicao, Orgao, Profissional, Projeto, Tarefa
from ..serializar import como_dict

router = APIRouter(prefix="/api", tags=["painel"])


def resumo_medicao(s: Session, contrato: Contrato) -> dict:
    por_situacao = {sit: float(s.scalar(select(func.coalesce(func.sum(Medicao.quantidade), 0))
                                        .where(Medicao.contrato_id == contrato.id, Medicao.situacao == sit)) or 0)
                    for sit in ("EXECUTADA", "ACEITA", "GLOSADA", "PAGA")}
    executado = por_situacao["EXECUTADA"] + por_situacao["ACEITA"] + por_situacao["PAGA"]
    aceito = por_situacao["ACEITA"] + por_situacao["PAGA"]
    contratado = float(contrato.quantidade_contratada) if contrato.quantidade_contratada is not None else None
    vu = float(contrato.valor_unitario) if contrato.valor_unitario is not None else None
    valor = (lambda q: round(q * vu, 2) if vu is not None else None)
    return {
        "contrato": como_dict(contrato), "unidade": contrato.unidade_outra if contrato.metrica == "OUTRA" else contrato.metrica,
        "contratado": contratado, "executado": executado, "aceito": aceito, "pago": por_situacao["PAGA"],
        "glosado": por_situacao["GLOSADA"], "saldo": round(contratado - executado, 2) if contratado is not None else None,
        "valor_executado": valor(executado), "valor_aceito": valor(aceito), "valor_pago": valor(por_situacao["PAGA"]),
    }


@router.get("/contratos/{contrato_id}/medicao")
def medicao_do_contrato(contrato_id: int, s: Session = Depends(sessao), _=Depends(usuario_atual)) -> dict:
    contrato = s.get(Contrato, contrato_id)
    if not contrato:
        raise HTTPException(404, "Contrato não encontrado")
    itens = s.scalars(select(Medicao).where(Medicao.contrato_id == contrato_id).order_by(Medicao.data_execucao))
    return {**resumo_medicao(s, contrato), "itens": [como_dict(i) for i in itens]}


@router.get("/painel")
def painel(s: Session = Depends(sessao), _=Depends(usuario_atual)) -> dict:
    contar = lambda modelo, *cond: s.scalar(select(func.count()).select_from(modelo).where(*cond))  # noqa: E731
    ultimos = s.scalars(select(ExecucaoStart).order_by(ExecucaoStart.em.desc()).limit(5))
    return {
        "orgaos": contar(Orgao), "contratos": contar(Contrato, Contrato.situacao == "ATIVO"),
        "projetos": contar(Projeto, Projeto.ativo.is_(True)), "profissionais": contar(Profissional, Profissional.ativo.is_(True)),
        "tarefas_abertas": contar(Tarefa, Tarefa.situacao != "CONCLUIDA"),
        "contratos_resumo": [resumo_medicao(s, c) for c in s.scalars(select(Contrato).order_by(Contrato.numero))],
        "ultimos_start": [como_dict(e) for e in ultimos],
    }
