"""Lançamento manual de horas, totais, inconsistências e aceite para faturamento."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import config
from ..acesso import ESCRITA, usuario_atual
from ..auditoria import registrar
from ..db import sessao
from ..esquemas import AceiteNovo, LancamentoNovo
from ..modelos import AceiteHoras, Agente, LancamentoHoras, Profissional
from ..serializar import como_dict
from ..servicos import horas as calculo

router = APIRouter(prefix="/api/horas", tags=["horas"])


def consultar(s: Session, mes: Optional[str] = None, profissional_id: Optional[int] = None,
              projeto_id: Optional[int] = None, contrato_id: Optional[int] = None) -> list[LancamentoHoras]:
    q = select(LancamentoHoras).order_by(LancamentoHoras.data, LancamentoHoras.inicio)
    if mes:
        ano, m = (int(x) for x in mes.split("-"))
        inicio = date(ano, m, 1)
        fim = date(ano + (m == 12), m % 12 + 1, 1)
        q = q.where(LancamentoHoras.data >= inicio, LancamentoHoras.data < fim)
    for coluna, valor in ((LancamentoHoras.profissional_id, profissional_id), (LancamentoHoras.projeto_id, projeto_id),
                          (LancamentoHoras.contrato_id, contrato_id)):
        if valor:
            q = q.where(coluna == valor)
    return list(s.scalars(q))


def ids_aceitos(s: Session) -> set[int]:
    return set(s.scalars(select(AceiteHoras.lancamento_id)))


def _validar_mes(mes: Optional[str]) -> None:
    if mes and not (len(mes) == 7 and mes[4] == "-" and mes[:4].isdigit() and 1 <= int(mes[5:]) <= 12):
        raise HTTPException(422, "Mês no formato AAAA-MM")


@router.get("")
def listar(mes: Optional[str] = None, profissional_id: Optional[int] = None, projeto_id: Optional[int] = None,
           contrato_id: Optional[int] = None, s: Session = Depends(sessao), _=Depends(usuario_atual)) -> list[dict]:
    _validar_mes(mes)
    aceitos = ids_aceitos(s)
    return [{**como_dict(l), "horas": calculo.horas_liquidas(l), "aceita": l.id in aceitos}
            for l in consultar(s, mes, profissional_id, projeto_id, contrato_id)]


@router.post("", status_code=201)
def lancar(dados: LancamentoNovo, s: Session = Depends(sessao), u=Depends(ESCRITA)) -> dict:
    if dados.profissional_id and not s.get(Profissional, dados.profissional_id):
        raise HTTPException(404, "Profissional não encontrado")
    if dados.agente_id and not s.get(Agente, dados.agente_id):
        raise HTTPException(404, "Agente não encontrado")
    l = LancamentoHoras(**dados.model_dump(), lancado_por=u.id)
    s.add(l)
    s.flush()
    registrar(s, u.id, "LANCAR_HORAS", "lancamento_horas", l.id, dados.model_dump(mode="json"))
    return {**como_dict(l), "horas": calculo.horas_liquidas(l)}


@router.patch("/{lancamento_id}")
def corrigir(lancamento_id: int, dados: LancamentoNovo, s: Session = Depends(sessao), u=Depends(ESCRITA)) -> dict:
    """Correção feita pelo responsável. O valor anterior fica na auditoria."""
    l = s.get(LancamentoHoras, lancamento_id)
    if not l:
        raise HTTPException(404, "Lançamento não encontrado")
    if lancamento_id in ids_aceitos(s):
        raise HTTPException(409, "Lançamento já aceito para faturamento: desfaça o aceite antes de corrigir")
    antes = como_dict(l)
    for k, v in dados.model_dump().items():
        setattr(l, k, v)
    registrar(s, u.id, "CORRIGIR_HORAS", "lancamento_horas", l.id, {"antes": antes, "depois": dados.model_dump(mode="json")})
    return {**como_dict(l), "horas": calculo.horas_liquidas(l)}


@router.delete("/{lancamento_id}", status_code=204)
def excluir(lancamento_id: int, s: Session = Depends(sessao), u=Depends(ESCRITA)) -> None:
    l = s.get(LancamentoHoras, lancamento_id)
    if not l:
        raise HTTPException(404, "Lançamento não encontrado")
    if lancamento_id in ids_aceitos(s):
        raise HTTPException(409, "Lançamento já aceito para faturamento não pode ser excluído")
    registrar(s, u.id, "EXCLUIR_HORAS", "lancamento_horas", l.id, como_dict(l))
    s.delete(l)


@router.post("/{lancamento_id}/aceite", status_code=201)
def aceitar(lancamento_id: int, dados: AceiteNovo, s: Session = Depends(sessao), u=Depends(ESCRITA)) -> dict:
    l = s.get(LancamentoHoras, lancamento_id)
    if not l:
        raise HTTPException(404, "Lançamento não encontrado")
    if l.tipo != "HUMANA":
        raise HTTPException(409, "Só horas humanas podem ser aceitas para faturamento")
    if lancamento_id in ids_aceitos(s):
        raise HTTPException(409, "Lançamento já aceito")
    aceite = AceiteHoras(lancamento_id=l.id, registrado_por=u.id, **dados.model_dump())
    s.add(aceite)
    s.flush()
    registrar(s, u.id, "ACEITAR_HORAS", "lancamento_horas", l.id, dados.model_dump(mode="json"))
    return como_dict(aceite)


@router.delete("/{lancamento_id}/aceite", status_code=204)
def desfazer_aceite(lancamento_id: int, s: Session = Depends(sessao), u=Depends(ESCRITA)) -> None:
    aceite = s.scalar(select(AceiteHoras).where(AceiteHoras.lancamento_id == lancamento_id))
    if not aceite:
        raise HTTPException(404, "Lançamento sem aceite")
    registrar(s, u.id, "DESFAZER_ACEITE", "lancamento_horas", lancamento_id, como_dict(aceite))
    s.delete(aceite)


@router.get("/resumo")
def resumo(mes: Optional[str] = None, profissional_id: Optional[int] = None, projeto_id: Optional[int] = None,
           contrato_id: Optional[int] = None, s: Session = Depends(sessao), _=Depends(usuario_atual)) -> dict:
    _validar_mes(mes)
    lancamentos = consultar(s, mes, profissional_id, projeto_id, contrato_id)
    inativos = set(s.scalars(select(Profissional.id).where(Profissional.ativo.is_(False))))
    return {**calculo.resumo(lancamentos, ids_aceitos(s)),
            "inconsistencias": calculo.inconsistencias(lancamentos, config.carregar().jornada_horas, inativos)}
