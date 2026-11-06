"""Atendimento: chamados, mudança de estado e exportação CSV."""
from __future__ import annotations

import csv
import io
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from ..acesso import exigir_perfil, usuario_atual
from ..comum import como_lista, now, registrar_auditoria
from ..db import connect
from ..esquemas import ChamadoNovo, EstadoDoChamado

router = APIRouter(prefix="/api", tags=["atendimento"])

_COLUNAS_PARA_LEITOR = "id, subject, priority, status, created_at, updated_at"


def celula_segura(valor: Any) -> Any:
    """Impede que a planilha execute o conteúdo da célula como fórmula (injeção em CSV)."""
    if isinstance(valor, str) and valor[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + valor
    return valor


@router.get("/tickets")
def listar_chamados(usuario: dict[str, Any] = Depends(usuario_atual)) -> list[dict[str, Any]]:
    # descrição e contato podem ter dados pessoais: o leitor não recebe
    colunas = _COLUNAS_PARA_LEITOR if usuario["role"] == "VIEWER" else "*"
    with connect() as c:
        return como_lista(c.execute(f"SELECT {colunas} FROM tickets ORDER BY id DESC").fetchall())


@router.post("/tickets", status_code=201)
def abrir_chamado(dados: ChamadoNovo, usuario: dict[str, Any] = Depends(exigir_perfil("ADMIN", "EDITOR"))) -> dict[str, Any]:
    with connect() as c:
        if dados.contact_id is not None and not c.execute("SELECT 1 FROM contacts WHERE id = ?", (dados.contact_id,)).fetchone():
            raise HTTPException(404, "Contato não encontrado")
        agora = now()
        cursor = c.execute(
            "INSERT INTO tickets (contact_id, subject, description, priority, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (dados.contact_id, dados.subject, dados.description, dados.priority, agora, agora),
        )
        registrar_auditoria(c, usuario["id"], "CREATE", "ticket", cursor.lastrowid)
        return {"id": cursor.lastrowid, "status": "ABERTO"}


@router.patch("/tickets/{chamado_id}/status")
def mudar_estado(
    chamado_id: int, dados: EstadoDoChamado, usuario: dict[str, Any] = Depends(exigir_perfil("ADMIN", "EDITOR"))
) -> dict[str, str]:
    with connect() as c:
        if not c.execute("SELECT 1 FROM tickets WHERE id = ?", (chamado_id,)).fetchone():
            raise HTTPException(404, "Chamado não encontrado")
        c.execute("UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?", (dados.status, now(), chamado_id))
        registrar_auditoria(c, usuario["id"], "UPDATE_STATUS", "ticket", chamado_id, {"status": dados.status})
    return {"status": dados.status}


@router.get("/export/tickets.csv")
def exportar_chamados(usuario: dict[str, Any] = Depends(exigir_perfil("ADMIN", "APPROVER"))) -> StreamingResponse:
    with connect() as c:
        linhas = c.execute("SELECT id, subject, priority, status, created_at, updated_at FROM tickets ORDER BY id").fetchall()
    saida = io.StringIO()
    saida.write("﻿")
    escritor = csv.writer(saida)
    escritor.writerow(["ID", "Assunto", "Prioridade", "Estado", "Criado em", "Atualizado em"])
    escritor.writerows(tuple(celula_segura(valor) for valor in linha) for linha in linhas)
    return StreamingResponse(
        iter([saida.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=chamados.csv"},
    )
