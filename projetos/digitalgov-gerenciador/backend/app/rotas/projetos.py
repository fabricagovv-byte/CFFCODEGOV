"""Situação real de cada projeto, START e testes importados."""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..acesso import ESCRITA, usuario_atual
from ..auditoria import registrar
from ..db import sessao
from ..modelos import ExecucaoStart, ExecucaoTeste, Projeto
from ..serializar import como_dict
from ..servicos import situacao, start

router = APIRouter(prefix="/api/projetos", tags=["projetos"])


def _projeto(s: Session, projeto_id: int) -> Projeto:
    p = s.get(Projeto, projeto_id)
    if not p:
        raise HTTPException(404, "Projeto não encontrado")
    return p


@router.get("/{projeto_id}/situacao")
def ver_situacao(projeto_id: int, s: Session = Depends(sessao), _=Depends(usuario_atual)) -> dict:
    p = _projeto(s, projeto_id)
    ultimo = s.scalar(select(ExecucaoTeste).where(ExecucaoTeste.projeto_id == p.id).order_by(ExecucaoTeste.executado_em.desc()))
    return {**situacao.completa(p), "testes": como_dict(ultimo) if ultimo else None,
            "agentes": "Integração pendente" if p.integracao_agentes != "CONFIGURADA" else "Integração pendente (conector não instalado)"}


@router.post("/{projeto_id}/start")
def acionar_start(projeto_id: int, s: Session = Depends(sessao), u=Depends(ESCRITA)) -> dict:
    p = _projeto(s, projeto_id)
    r = start.executar(s, p)
    execucao = ExecucaoStart(projeto_id=p.id, usuario_id=u.id, resultado=r["resultado"], etapas=json.dumps(r["etapas"], ensure_ascii=False))
    s.add(execucao)
    s.flush()
    registrar(s, u.id, "START", "projeto", p.id, {"resultado": r["resultado"]})
    return {"id": execucao.id, **r}


@router.get("/{projeto_id}/starts")
def historico_start(projeto_id: int, s: Session = Depends(sessao), _=Depends(usuario_atual)) -> list[dict]:
    q = select(ExecucaoStart).where(ExecucaoStart.projeto_id == projeto_id).order_by(ExecucaoStart.em.desc()).limit(50)
    return [{**como_dict(e), "etapas": json.loads(e.etapas)} for e in s.scalars(q)]


@router.post("/{projeto_id}/testes", status_code=201)
async def importar_testes(projeto_id: int, arquivo: UploadFile = File(...), s: Session = Depends(sessao), u=Depends(ESCRITA)) -> dict:
    """Recebe o resultado real dos testes (JUnit XML gerado pelo pytest, Jest, Maven etc.)."""
    p = _projeto(s, projeto_id)
    try:
        raiz = ET.fromstring(await arquivo.read(5 * 1024 * 1024))
    except ET.ParseError:
        raise HTTPException(422, "Arquivo não é um XML JUnit válido")
    suites = [raiz] if raiz.tag == "testsuite" else list(raiz.iter("testsuite"))
    casos = [c for suite in suites for c in suite.iter("testcase")]
    if not casos:
        raise HTTPException(422, "Nenhum caso de teste no arquivo")
    conta = lambda tag: sum(1 for c in casos if c.find(tag) is not None)  # noqa: E731
    execucao = ExecucaoTeste(projeto_id=p.id, origem=(arquivo.filename or "junit.xml")[:200], total=len(casos),
                             falhas=conta("failure"), erros=conta("error"), ignorados=conta("skipped"))
    s.add(execucao)
    s.flush()
    registrar(s, u.id, "IMPORTAR_TESTES", "projeto", p.id, como_dict(execucao))
    return como_dict(execucao)


@router.get("/{projeto_id}/testes")
def listar_testes(projeto_id: int, s: Session = Depends(sessao), _=Depends(usuario_atual)) -> list[dict]:
    q = select(ExecucaoTeste).where(ExecucaoTeste.projeto_id == projeto_id).order_by(ExecucaoTeste.executado_em.desc())
    return [como_dict(e) for e in s.scalars(q)]
