"""Relatórios (Word, PDF, Excel) e exportação de qualquer cadastro para Excel."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import config
from ..acesso import usuario_atual
from ..db import sessao
from ..modelos import Agente, Contrato, LancamentoHoras, Medicao, Orgao, Profissional, Projeto
from ..serializar import como_dict
from ..servicos import horas as calculo
from ..servicos.relatorios import Relatorio, brl
from .cadastros import CADASTROS
from .horas import consultar, ids_aceitos

router = APIRouter(prefix="/api/relatorios", tags=["relatórios"])

FORMATOS = {"docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pdf": "application/pdf", "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}


def _entregar(rel: Relatorio, formato: str, nome: str) -> Response:
    if formato not in FORMATOS:
        raise HTTPException(422, "Formato: docx, pdf ou xlsx")
    corpo = {"docx": rel.word, "pdf": rel.pdf, "xlsx": rel.excel}[formato]()
    return Response(corpo, media_type=FORMATOS[formato], headers={"Content-Disposition": f'attachment; filename="{nome}.{formato}"'})


@router.get("/horas.{formato}")
def relatorio_horas(formato: str, mes: str, projeto_id: Optional[int] = None, contrato_id: Optional[int] = None,
                    s: Session = Depends(sessao), _=Depends(usuario_atual)) -> Response:
    lancs = consultar(s, mes, None, projeto_id, contrato_id)
    aceitos = ids_aceitos(s)
    pessoas = {p.id: p for p in s.scalars(select(Profissional))}
    agentes = {a.id: a for a in s.scalars(select(Agente))}
    inativos = {p.id for p in pessoas.values() if not p.ativo}
    resumo = calculo.resumo(lancs, aceitos)
    nome = lambda tipo, id_: (pessoas[id_].nome if tipo == "profissional" else f"{agentes[id_].codigo} {agentes[id_].nome}")  # noqa: E731
    rel = Relatorio(f"Relatório de horas — {mes[5:]}/{mes[:4]}", "Horas preenchidas pelo responsável. Horas de IA, humanas e aceitas ficam separadas.")
    rel.secao("Totais do mês").tabela(["Horas humanas registradas", "Horas humanas aceitas", "Horas de IA"],
                                      [[resumo["total"]["humanas"], resumo["total"]["aceitas"], resumo["total"]["ia"]]])
    rel.secao("Por profissional e agente").tabela(
        ["Quem", "Tipo", "Humanas", "Aceitas", "IA"],
        [[nome(r["tipo"], r["id"]), "Profissional" if r["tipo"] == "profissional" else "Agente (IA)", r["humanas"], r["aceitas"], r["ia"]]
         for r in resumo["por_mes"]])
    rel.secao("Por dia").tabela(["Data", "Quem", "Humanas", "Aceitas", "IA"],
                                [[f"{r['data'][8:]}/{r['data'][5:7]}/{r['data'][:4]}", nome(r["tipo"], r["id"]), r["humanas"], r["aceitas"], r["ia"]]
                                 for r in resumo["por_dia"]])
    achados = calculo.inconsistencias(lancs, config.carregar().jornada_horas, inativos)
    rel.secao("Inconsistências para conferir")
    if achados:
        rel.tabela(["Tipo", "Descrição", "Lançamentos"], [[a["tipo"], a["mensagem"], ", ".join(map(str, a["lancamentos"]))] for a in achados])
    else:
        rel.texto("Nenhuma inconsistência encontrada.")
    rel.secao("Lançamentos").tabela(
        ["Nº", "Data", "Tipo", "Quem", "Início", "Fim", "Intervalo (min)", "Horas", "Aceita", "Atividade"],
        [[l.id, f"{l.data:%d/%m/%Y}", l.tipo, nome("profissional" if l.tipo == "HUMANA" else "agente", l.profissional_id or l.agente_id),
          f"{l.inicio:%H:%M}", f"{l.fim:%H:%M}", l.intervalo_min, calculo.horas_liquidas(l), "Sim" if l.id in aceitos else "Não", l.atividade]
         for l in lancs])
    return _entregar(rel, formato, f"horas_{mes}")


@router.get("/medicao/{contrato_id}.{formato}")
def relatorio_medicao(contrato_id: int, formato: str, s: Session = Depends(sessao), _=Depends(usuario_atual)) -> Response:
    from .painel import resumo_medicao
    contrato = s.get(Contrato, contrato_id)
    if not contrato:
        raise HTTPException(404, "Contrato não encontrado")
    orgao = s.get(Orgao, contrato.orgao_id)
    r = resumo_medicao(s, contrato)
    u = r["unidade"]
    rel = Relatorio(f"Relatório de medição — contrato {contrato.numero}", f"{orgao.nome if orgao else ''} · {contrato.objeto}")
    rel.secao("Situação do contrato").tabela(
        ["Contratado", "Executado", "Aceito", "Pago", "Glosado", "Saldo", "Valor executado", "Valor aceito"],
        [[f"{r['contratado'] or 0:g} {u}", f"{r['executado']:g} {u}", f"{r['aceito']:g} {u}", f"{r['pago']:g} {u}",
          f"{r['glosado']:g} {u}", f"{r['saldo']:g} {u}" if r["saldo"] is not None else "—", brl(r["valor_executado"]), brl(r["valor_aceito"])]])
    itens = list(s.scalars(select(Medicao).where(Medicao.contrato_id == contrato_id).order_by(Medicao.data_execucao)))
    rel.secao("Itens medidos").tabela(["Data", "Item", "Descrição", "Quantidade", "Situação", "Documento de aceite"],
                                      [[f"{i.data_execucao:%d/%m/%Y}", i.item, i.descricao, f"{float(i.quantidade):g} {u}", i.situacao,
                                        i.documento_aceite or "—"] for i in itens])
    rel.texto("Quantidade aceita só com documento do órgão. Executado sem aceite aguarda conferência.")
    return _entregar(rel, formato, f"medicao_{contrato.numero}".replace("/", "-"))


@router.get("/exportar/{cadastro}.xlsx")
def exportar(cadastro: str, s: Session = Depends(sessao), _=Depends(usuario_atual)) -> Response:
    if cadastro == "horas":
        aceitos = ids_aceitos(s)
        linhas = [{**como_dict(l), "horas": calculo.horas_liquidas(l), "aceita": l.id in aceitos}
                  for l in s.scalars(select(LancamentoHoras).order_by(LancamentoHoras.data))]
    elif cadastro in CADASTROS:
        modelo = CADASTROS[cadastro][0]
        linhas = [como_dict(o) for o in s.scalars(select(modelo).order_by(modelo.id))]
    else:
        raise HTTPException(404, "Cadastro desconhecido")
    cab = list(linhas[0].keys()) if linhas else ["sem registros"]
    rel = Relatorio(cadastro).secao(cadastro).tabela(cab, [[l.get(c) for c in cab] for l in linhas])
    return _entregar(rel, "xlsx", cadastro)
