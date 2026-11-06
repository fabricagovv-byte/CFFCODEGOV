"""MOD-006 — Auditoria."""
import pytest
from sqlalchemy import text

from app.db import engine
from tests.conftest import EH_PG, PDF_MINIMO, criar_doc


def _acoes(client, h, **filtros):
    r = client.get("/api/auditoria", params=filtros, headers=h)
    assert r.status_code == 200, r.text
    return [i["acao"] for i in r.json()["itens"]]


def test_acoes_sensiveis_sao_auditadas(client, usuarios):
    h = usuarios["GESTOR"]
    d = criar_doc(client, h, classificacao="RESTRITO")
    client.patch(f"/api/documentos/{d['id']}", json={"titulo": "Novo título"}, headers=h)
    a = client.post(f"/api/documentos/{d['id']}/arquivos", files={"arquivo": ("a.pdf", PDF_MINIMO, "application/pdf")}, headers=h).json()
    client.get(f"/api/arquivos/{a['id']}", headers=h)
    client.get(f"/api/documentos/{d['id']}", headers=h)
    client.delete(f"/api/documentos/{d['id']}", headers=h)
    client.post("/api/auth/login", json={"email": "gestor@teste.gov.br", "senha": "errada"})
    acoes = set(_acoes(client, usuarios["ADMIN"], por_pagina=200))
    for esperado in ("LOGIN", "LOGIN_FALHA", "DOCUMENTO_CRIADO", "DOCUMENTO_ALTERADO", "ARQUIVO_ENVIADO",
                     "ARQUIVO_BAIXADO", "DOCUMENTO_CONSULTADO", "DOCUMENTO_ARQUIVADO"):
        assert esperado in acoes, esperado


def test_registro_tem_ip_usuario_e_detalhes(client, usuarios):
    criar_doc(client, usuarios["GESTOR"])
    r = client.get("/api/auditoria", params={"acao": "DOCUMENTO_CRIADO"}, headers=usuarios["ADMIN"]).json()
    item = r["itens"][0]
    assert item["usuario_id"] and item["ip"] and "numero" in item["detalhes"]


def test_auditoria_somente_admin_e_gestor(client, usuarios):
    assert client.get("/api/auditoria", headers=usuarios["OPERADOR"]).status_code == 403
    assert client.get("/api/auditoria", headers=usuarios["CONSULTA"]).status_code == 403


def test_nao_existe_rota_para_alterar_auditoria(client, usuarios):
    assert client.delete("/api/auditoria/1", headers=usuarios["ADMIN"]).status_code in (404, 405)
    assert client.patch("/api/auditoria/1", json={}, headers=usuarios["ADMIN"]).status_code in (404, 405)


def test_upload_rejeitado_e_auditado(client, usuarios):
    d = criar_doc(client, usuarios["GESTOR"])
    client.post(f"/api/documentos/{d['id']}/arquivos", files={"arquivo": ("x.pdf", b"nao-pdf", "application/pdf")}, headers=usuarios["GESTOR"])
    assert "UPLOAD_REJEITADO" in _acoes(client, usuarios["ADMIN"])


@pytest.mark.skipif(not EH_PG, reason="trigger de imutabilidade existe só no PostgreSQL")
def test_trigger_impede_update_e_delete_no_postgres(client, usuarios):
    criar_doc(client, usuarios["GESTOR"])
    for sql in ("UPDATE auditoria SET acao='X'", "DELETE FROM auditoria"):
        with pytest.raises(Exception, match="somente inserção"):
            with engine.begin() as c:
                c.execute(text(sql))
