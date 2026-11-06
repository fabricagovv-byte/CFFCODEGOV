def test_login_e_dados_do_usuario(cliente, entrar):
    h = entrar()
    assert cliente.get("/api/eu", headers=h).json()["perfil"] == "ADMIN"


def test_sem_login_nao_entra(cliente):
    assert cliente.get("/api/contratos").status_code == 401


def test_senha_errada(cliente, entrar):
    entrar()
    assert cliente.post("/api/login", json={"login": "admin", "senha": "errada-errada-1"}).status_code == 401


def test_bloqueio_apos_cinco_erros(cliente, entrar):
    entrar()
    for i in range(5):
        cliente.post("/api/login", json={"login": "admin", "senha": f"errada-{i}-xxxxx"})
    assert cliente.post("/api/login", json={"login": "admin", "senha": "senha-de-teste-123"}).status_code == 429


def test_sair_encerra_a_sessao(cliente, entrar):
    h = entrar()
    assert cliente.post("/api/logout", headers=h).status_code == 200
    assert cliente.get("/api/eu", headers=h).status_code == 401


def test_perfil_consulta_nao_altera(cliente, entrar):
    h = entrar("leitor", "CONSULTA")
    assert cliente.get("/api/orgaos", headers=h).status_code == 200
    assert cliente.post("/api/orgaos", headers=h, json={"nome": "Órgão"}).status_code == 403


def test_so_admin_exclui_e_cria_usuario(cliente, entrar):
    adm = entrar()
    gestor = entrar("gestor", "GESTOR")
    org = cliente.post("/api/orgaos", headers=gestor, json={"nome": "Órgão X"}).json()
    assert cliente.delete(f"/api/orgaos/{org['id']}", headers=gestor).status_code == 403
    assert cliente.post("/api/usuarios", headers=gestor, json={"nome": "Novo", "login": "novo", "senha": "x" * 12, "perfil": "GESTOR"}).status_code == 403
    assert cliente.post("/api/usuarios", headers=adm, json={"nome": "Novo", "login": "novo", "senha": "x" * 12, "perfil": "GESTOR"}).status_code == 201
    assert cliente.delete(f"/api/orgaos/{org['id']}", headers=adm).status_code == 204


def test_senha_guardada_com_scrypt_e_sem_aparecer(cliente, entrar):
    h = entrar()
    usuarios = cliente.get("/api/usuarios", headers=h).json()
    assert all("senha_hash" not in u for u in usuarios)
    from app.db import _fabrica_sessoes
    from app.modelos import Usuario
    with _fabrica_sessoes()() as s:
        assert s.query(Usuario).first().senha_hash.startswith("scrypt$")
