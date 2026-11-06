def test_saude_mostra_a_migracao(cliente):
    r = cliente.get("/health").json()
    assert r["status"] == "ok" and r["migracao"] == "0001"


def test_registro_e_gravado_no_banco(cliente):
    assert cliente.post("/api/registros", json={"titulo": "Primeiro registro"}).status_code == 201
    assert cliente.get("/api/registros").json()[0]["titulo"] == "Primeiro registro"
    assert cliente.post("/api/registros", json={"titulo": "x"}).status_code == 422


def test_start_exige_o_token_do_gerenciador(cliente):
    assert cliente.post("/api/gerenciador/start").status_code == 401
    assert cliente.post("/api/gerenciador/start", headers={"Authorization": "Bearer errado"}).status_code == 401
    r = cliente.post("/api/gerenciador/start", headers={"Authorization": "Bearer " + "t" * 40})
    assert r.status_code == 200 and "Ciclo de produção nº 1" in r.json()["mensagem"]


def test_migracoes_vao_e_voltam():
    from conftest import alembic
    alembic("downgrade", "base")
    alembic("upgrade", "head")
    alembic("check")
