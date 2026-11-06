"""Rotas de cadastro geradas a partir do modelo e do esquema: listar, ver, criar, alterar e excluir."""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import create_model
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import esquemas as e
from .. import modelos as m
from ..acesso import ESCRITA, SO_ADMIN, usuario_atual
from ..auditoria import registrar
from ..db import sessao
from ..serializar import como_dict

router = APIRouter(prefix="/api", tags=["cadastros"])

# caminho → (modelo, esquema, ordem da listagem)
CADASTROS: dict[str, tuple[type, type, Any]] = {
    "orgaos": (m.Orgao, e.OrgaoNovo, m.Orgao.nome),
    "contratos": (m.Contrato, e.ContratoNovo, m.Contrato.numero),
    "ordens-servico": (m.OrdemServico, e.OrdemServicoNova, m.OrdemServico.numero),
    "projetos": (m.Projeto, e.ProjetoNovo, m.Projeto.codigo),
    "profissionais": (m.Profissional, e.ProfissionalNovo, m.Profissional.nome),
    "agentes": (m.Agente, e.AgenteNovo, m.Agente.codigo),
    "tarefas": (m.Tarefa, e.TarefaNova, m.Tarefa.id.desc()),
    "evidencias": (m.Evidencia, e.EvidenciaNova, m.Evidencia.id.desc()),
    "medicoes": (m.Medicao, e.MedicaoNova, m.Medicao.data_execucao.desc()),
}


def _parcial(esquema: type) -> type:
    """Mesmo esquema com todos os campos opcionais (para alterações parciais)."""
    campos = {nome: (Optional[info.annotation], None) for nome, info in esquema.model_fields.items()}
    return create_model(f"{esquema.__name__}Parcial", __base__=e.Base, **campos)


def _filtros(modelo: type, request: Request) -> list:
    """Filtro simples por igualdade nos campos *_id e situacao/tipo (ex.: ?contrato_id=3)."""
    condicoes = []
    for chave, valor in request.query_params.items():
        coluna = getattr(modelo, chave, None)
        if coluna is not None and (chave.endswith("_id") or chave in ("situacao", "tipo", "ativo")):
            condicoes.append(coluna == (int(valor) if chave.endswith("_id") else (valor == "true") if chave == "ativo" else valor))
    return condicoes


def _registrar_rotas(caminho: str, modelo: type, esquema: type, ordem: Any) -> None:
    parcial = _parcial(esquema)
    entidade = caminho.replace("-", "_")

    def buscar(s: Session, id_: int):
        obj = s.get(modelo, id_)
        if not obj:
            raise HTTPException(404, "Registro não encontrado")
        return obj

    @router.get(f"/{caminho}", name=f"listar_{entidade}")
    def listar(request: Request, s: Session = Depends(sessao), _=Depends(usuario_atual)) -> list[dict]:
        return [como_dict(o) for o in s.scalars(select(modelo).where(*_filtros(modelo, request)).order_by(ordem))]

    @router.get(f"/{caminho}/{{id_}}", name=f"ver_{entidade}")
    def ver(id_: int, s: Session = Depends(sessao), _=Depends(usuario_atual)) -> dict:
        return como_dict(buscar(s, id_))

    @router.post(f"/{caminho}", status_code=201, name=f"criar_{entidade}")
    def criar(dados: esquema, s: Session = Depends(sessao), u=Depends(ESCRITA)) -> dict:  # type: ignore[valid-type]
        obj = modelo(**dados.model_dump())
        s.add(obj)
        s.flush()
        registrar(s, u.id, "CRIAR", entidade, obj.id, dados.model_dump(mode="json"))
        return como_dict(obj)

    @router.patch(f"/{caminho}/{{id_}}", name=f"alterar_{entidade}")
    def alterar(id_: int, dados: parcial, s: Session = Depends(sessao), u=Depends(ESCRITA)) -> dict:  # type: ignore[valid-type]
        obj = buscar(s, id_)
        mudancas = dados.model_dump(exclude_unset=True)
        antes = {k: getattr(obj, k) for k in mudancas}
        completo = {**como_dict(obj), **dados.model_dump(mode="json", exclude_unset=True)}
        esquema.model_validate({k: v for k, v in completo.items() if k in esquema.model_fields})  # regras do registro inteiro
        for k, v in mudancas.items():
            setattr(obj, k, v)
        registrar(s, u.id, "ALTERAR", entidade, id_, {"antes": antes, "depois": mudancas})
        return como_dict(obj)

    @router.delete(f"/{caminho}/{{id_}}", status_code=204, name=f"excluir_{entidade}")
    def excluir(id_: int, s: Session = Depends(sessao), u=Depends(SO_ADMIN)) -> None:
        obj = buscar(s, id_)
        registrar(s, u.id, "EXCLUIR", entidade, id_, como_dict(obj))
        s.delete(obj)


for _caminho, (_modelo, _esquema, _ordem) in CADASTROS.items():
    _registrar_rotas(_caminho, _modelo, _esquema, _ordem)
