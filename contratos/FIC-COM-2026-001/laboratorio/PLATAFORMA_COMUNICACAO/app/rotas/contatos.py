"""Contatos e consentimento (dados pessoais: leitor não acessa)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from ..acesso import exigir_perfil
from ..comum import como_lista, now, registrar_auditoria
from ..db import connect
from ..esquemas import ContatoNovo

router = APIRouter(prefix="/api/contacts", tags=["contatos"])


@router.get("")
def listar_contatos(usuario: dict[str, Any] = Depends(exigir_perfil("ADMIN", "EDITOR", "APPROVER"))) -> list[dict[str, Any]]:
    with connect() as c:
        return como_lista(
            c.execute("SELECT id, name, email, category, consent, created_at FROM contacts ORDER BY id DESC").fetchall()
        )


@router.post("", status_code=201)
def criar_contato(dados: ContatoNovo, usuario: dict[str, Any] = Depends(exigir_perfil("ADMIN", "EDITOR"))) -> dict[str, Any]:
    with connect() as c:
        cursor = c.execute(
            "INSERT INTO contacts (name, email, category, consent, created_at) VALUES (?, ?, ?, ?, ?)",
            (dados.name, dados.email, dados.category, int(dados.consent), now()),
        )
        registrar_auditoria(c, usuario["id"], "CREATE", "contact", cursor.lastrowid)
        return {"id": cursor.lastrowid, "consent": dados.consent}
