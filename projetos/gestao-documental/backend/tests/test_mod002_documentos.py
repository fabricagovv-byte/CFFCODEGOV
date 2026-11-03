"""MOD-002 — Cadastro documental."""
from tests.conftest import criar_doc


def test_criar_documento_gera_numero_unico(client, usuarios):
    a = criar_doc(client, usuarios["OPERADOR"])
    b = criar_doc(client, usuarios["OPERADOR"], titulo="Outro ofício")
    assert a["numero"] != b["numero"] and "/" in a["numero"]
    assert a["status"] == "ATIVO"


def test_validacao_de_campos(client, usuarios):
    r = client.post("/api/documentos", json={"titulo": "  ", "tipo": "x"}, headers=usuarios["OPERADOR"])
    assert r.status_code == 422
    r = client.post("/api/documentos", json={"titulo": "Válido", "tipo": "Ofício", "classificacao": "SECRETO"},
                    headers=usuarios["OPERADOR"])
    assert r.status_code == 422


def test_consulta_nao_cria(client, usuarios):
    r = client.post("/api/documentos", json={"titulo": "Teste", "tipo": "Ofício"}, headers=usuarios["CONSULTA"])
    assert r.status_code == 403


def test_operador_nao_cria_sigiloso(client, usuarios):
    r = client.post("/api/documentos", json={"titulo": "Teste", "tipo": "Ofício", "classificacao": "SIGILOSO"},
                    headers=usuarios["OPERADOR"])
    assert r.status_code == 403


def test_visibilidade_por_classificacao(client, usuarios):
    pub = criar_doc(client, usuarios["GESTOR"], classificacao="PUBLICO")
    res = criar_doc(client, usuarios["GESTOR"], classificacao="RESTRITO")
    sig = criar_doc(client, usuarios["GESTOR"], classificacao="SIGILOSO")
    ids = lambda h: {d["id"] for d in client.get("/api/documentos", headers=h).json()["itens"]}  # noqa: E731
    assert ids(usuarios["CONSULTA"]) == {pub["id"]}
    assert ids(usuarios["OPERADOR"]) == {pub["id"], res["id"]}
    assert ids(usuarios["GESTOR"]) == {pub["id"], res["id"], sig["id"]}
    assert client.get(f"/api/documentos/{sig['id']}", headers=usuarios["OPERADOR"]).status_code == 404


def test_editar_e_arquivar(client, usuarios):
    d = criar_doc(client, usuarios["OPERADOR"])
    r = client.patch(f"/api/documentos/{d['id']}", json={"titulo": "Título corrigido"}, headers=usuarios["OPERADOR"])
    assert r.status_code == 200 and r.json()["titulo"] == "Título corrigido"
    assert client.patch(f"/api/documentos/{d['id']}", json={"status": "ARQUIVADO"},
                        headers=usuarios["OPERADOR"]).status_code == 403
    assert client.delete(f"/api/documentos/{d['id']}", headers=usuarios["OPERADOR"]).status_code == 403
    assert client.delete(f"/api/documentos/{d['id']}", headers=usuarios["GESTOR"]).status_code == 204
    assert client.get(f"/api/documentos/{d['id']}", headers=usuarios["GESTOR"]).json()["status"] == "ARQUIVADO"


def test_paginacao(client, usuarios):
    for i in range(5):
        criar_doc(client, usuarios["OPERADOR"], titulo=f"Documento {i}")
    r = client.get("/api/documentos?pagina=2&por_pagina=2", headers=usuarios["OPERADOR"]).json()
    assert r["total"] == 5 and len(r["itens"]) == 2 and r["pagina"] == 2
    assert client.get("/api/documentos?por_pagina=1000", headers=usuarios["OPERADOR"]).status_code == 422


def test_documento_inexistente(client, usuarios):
    assert client.get("/api/documentos/99999", headers=usuarios["ADMIN"]).status_code == 404


def test_operador_nao_desarquiva_nem_reclassifica(client, usuarios):
    d = criar_doc(client, usuarios["OPERADOR"], classificacao="RESTRITO")
    assert client.patch(f"/api/documentos/{d['id']}", json={"classificacao": "PUBLICO"},
                        headers=usuarios["OPERADOR"]).status_code == 403
    client.delete(f"/api/documentos/{d['id']}", headers=usuarios["GESTOR"])
    assert client.patch(f"/api/documentos/{d['id']}", json={"status": "ATIVO"},
                        headers=usuarios["OPERADOR"]).status_code == 403
    assert client.patch(f"/api/documentos/{d['id']}", json={"status": "ATIVO"},
                        headers=usuarios["GESTOR"]).status_code == 200


def test_patch_com_null_e_espacos(client, usuarios):
    d = criar_doc(client, usuarios["OPERADOR"])
    r = client.patch(f"/api/documentos/{d['id']}", json={"titulo": None}, headers=usuarios["OPERADOR"])
    assert r.status_code == 200 and r.json()["titulo"] == d["titulo"]
    assert client.patch(f"/api/documentos/{d['id']}", json={"titulo": "     "}, headers=usuarios["OPERADOR"]).status_code == 422
