"""MOD-005 — Painel administrativo."""
from tests.conftest import PDF_MINIMO, criar_doc


def test_painel_indicadores(client, usuarios):
    h = usuarios["GESTOR"]
    d = criar_doc(client, h, tipo="Ofício")
    criar_doc(client, h, tipo="Portaria", classificacao="RESTRITO")
    client.post(f"/api/documentos/{d['id']}/arquivos", files={"arquivo": ("a.pdf", PDF_MINIMO, "application/pdf")}, headers=h)
    r = client.get("/api/painel/resumo", headers=h)
    assert r.status_code == 200
    p = r.json()
    assert p["documentos_total"] == 2
    assert p["documentos_por_tipo"] == {"Ofício": 1, "Portaria": 1}
    assert p["documentos_por_classificacao"] == {"PUBLICO": 1, "RESTRITO": 1}
    assert p["arquivos_total"] == 1 and p["armazenamento_bytes"] == len(PDF_MINIMO)
    assert p["usuarios_ativos"] == 4
    assert p["usuarios_por_perfil"]["ADMIN"] == 1
    assert len(p["ultimas_acoes"]) > 0


def test_painel_restrito_a_admin_e_gestor(client, usuarios):
    assert client.get("/api/painel/resumo", headers=usuarios["ADMIN"]).status_code == 200
    assert client.get("/api/painel/resumo", headers=usuarios["OPERADOR"]).status_code == 403
    assert client.get("/api/painel/resumo", headers=usuarios["CONSULTA"]).status_code == 403
