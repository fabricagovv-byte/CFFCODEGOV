"""Publicações com fluxo editorial: rascunho → revisão → aprovação por outra pessoa → publicação."""
from __future__ import annotations

import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ..acesso import exigir_perfil, usuario_atual
from ..comum import como_lista, now, registrar_auditoria
from ..db import connect
from ..esquemas import PublicacaoNova

router = APIRouter(prefix="/api/posts", tags=["publicações"])

_CONSULTA = (
    "SELECT p.*, ch.name AS channel, us.name AS author FROM posts p "
    "JOIN channels ch ON ch.id = p.channel_id JOIN users us ON us.id = p.author_id"
)


def _buscar(c: sqlite3.Connection, publicacao_id: int) -> sqlite3.Row:
    publicacao = c.execute("SELECT * FROM posts WHERE id = ?", (publicacao_id,)).fetchone()
    if not publicacao:
        raise HTTPException(404, "Publicação não encontrada")
    return publicacao


@router.get("")
def listar_publicacoes(usuario: dict[str, Any] = Depends(usuario_atual)) -> list[dict[str, Any]]:
    # o leitor só vê o que já foi publicado
    filtro = " WHERE p.status = 'PUBLICADO'" if usuario["role"] == "VIEWER" else ""
    with connect() as c:
        return como_lista(c.execute(_CONSULTA + filtro + " ORDER BY p.id DESC").fetchall())


@router.post("", status_code=201)
def criar_publicacao(
    dados: PublicacaoNova, usuario: dict[str, Any] = Depends(exigir_perfil("ADMIN", "EDITOR"))
) -> dict[str, Any]:
    with connect() as c:
        if not c.execute("SELECT 1 FROM channels WHERE id = ?", (dados.channel_id,)).fetchone():
            raise HTTPException(404, "Canal não encontrado")
        agora = now()
        cursor = c.execute(
            "INSERT INTO posts (channel_id, title, body, status, author_id, created_at, updated_at) "
            "VALUES (?, ?, ?, 'RASCUNHO', ?, ?, ?)",
            (dados.channel_id, dados.title, dados.body, usuario["id"], agora, agora),
        )
        registrar_auditoria(c, usuario["id"], "CREATE", "post", cursor.lastrowid)
        return {"id": cursor.lastrowid, "status": "RASCUNHO"}


@router.post("/{publicacao_id}/submit")
def enviar_para_revisao(
    publicacao_id: int, usuario: dict[str, Any] = Depends(exigir_perfil("ADMIN", "EDITOR"))
) -> dict[str, str]:
    with connect() as c:
        publicacao = _buscar(c, publicacao_id)
        if publicacao["author_id"] != usuario["id"] and usuario["role"] != "ADMIN":
            raise HTTPException(403, "Somente autor ou gestor")
        if publicacao["status"] != "RASCUNHO":
            raise HTTPException(409, "Estado inválido")
        c.execute("UPDATE posts SET status = 'EM_REVISAO', updated_at = ? WHERE id = ?", (now(), publicacao_id))
        registrar_auditoria(c, usuario["id"], "SUBMIT", "post", publicacao_id)
    return {"status": "EM_REVISAO"}


@router.post("/{publicacao_id}/approve")
def aprovar(publicacao_id: int, usuario: dict[str, Any] = Depends(exigir_perfil("ADMIN", "APPROVER"))) -> dict[str, str]:
    with connect() as c:
        publicacao = _buscar(c, publicacao_id)
        if publicacao["status"] != "EM_REVISAO":
            raise HTTPException(409, "A publicação não está em revisão")
        if publicacao["author_id"] == usuario["id"]:
            raise HTTPException(409, "Aprovação deve ser feita por outra pessoa")
        c.execute(
            "UPDATE posts SET status = 'APROVADO', approver_id = ?, updated_at = ? WHERE id = ?",
            (usuario["id"], now(), publicacao_id),
        )
        registrar_auditoria(c, usuario["id"], "APPROVE", "post", publicacao_id)
    return {"status": "APROVADO"}


@router.post("/{publicacao_id}/publish")
def publicar(publicacao_id: int, usuario: dict[str, Any] = Depends(exigir_perfil("ADMIN", "APPROVER"))) -> dict[str, str]:
    with connect() as c:
        publicacao = _buscar(c, publicacao_id)
        if publicacao["status"] != "APROVADO":
            raise HTTPException(409, "Aprovação obrigatória")
        agora = now()
        c.execute(
            "UPDATE posts SET status = 'PUBLICADO', published_at = ?, updated_at = ? WHERE id = ?",
            (agora, agora, publicacao_id),
        )
        registrar_auditoria(c, usuario["id"], "PUBLISH", "post", publicacao_id)
    # o envio por e-mail/SMS depende de provedor contratado e ainda não existe
    return {"status": "PUBLICADO", "published_at": agora, "external_delivery": "NAO_EXECUTADA"}
