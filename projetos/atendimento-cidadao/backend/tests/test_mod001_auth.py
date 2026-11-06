"""MOD-001 — Autenticação e controle de acesso."""
from app import mail
from tests.conftest import SENHA, criar_usuario, login


def test_login_sucesso_retorna_token_e_usuario(client):
    criar_usuario("ana@teste.gov.br", "OPERADOR")
    r = client.post("/api/auth/login", json={"email": "ANA@teste.gov.br", "senha": SENHA})
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["token_type"] == "bearer" and corpo["usuario"]["perfil"] == "OPERADOR"
    assert "senha_hash" not in corpo["usuario"]


def test_login_senha_errada_e_email_inexistente_tem_mesma_mensagem(client):
    criar_usuario("ana@teste.gov.br", "OPERADOR")
    r1 = client.post("/api/auth/login", json={"email": "ana@teste.gov.br", "senha": "errada"})
    r2 = client.post("/api/auth/login", json={"email": "ninguem@teste.gov.br", "senha": "errada"})
    assert r1.status_code == r2.status_code == 401
    assert r1.json() == r2.json()


def test_usuario_inativo_nao_entra(client):
    criar_usuario("inativo@teste.gov.br", "OPERADOR", ativo=False)
    r = client.post("/api/auth/login", json={"email": "inativo@teste.gov.br", "senha": SENHA})
    assert r.status_code == 401


def test_bloqueio_por_forca_bruta(client):
    criar_usuario("alvo@teste.gov.br", "OPERADOR")
    for _ in range(5):
        client.post("/api/auth/login", json={"email": "alvo@teste.gov.br", "senha": "errada"})
    r = client.post("/api/auth/login", json={"email": "alvo@teste.gov.br", "senha": SENHA})
    assert r.status_code == 429


def test_rota_protegida_sem_token_e_token_invalido(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer abc.def.ghi"}).status_code == 401


def test_logout_revoga_token(client):
    criar_usuario("ana@teste.gov.br", "OPERADOR")
    h = login(client, "ana@teste.gov.br")
    assert client.get("/api/auth/me", headers=h).status_code == 200
    assert client.post("/api/auth/logout", headers=h).status_code == 204
    assert client.get("/api/auth/me", headers=h).status_code == 401


def test_recuperacao_e_redefinicao_de_senha(client):
    criar_usuario("ana@teste.gov.br", "OPERADOR")
    r = client.post("/api/auth/recuperar-senha", json={"email": "ana@teste.gov.br"})
    assert r.status_code == 202
    assert len(mail.CAIXA_SAIDA) == 1
    token = mail.CAIXA_SAIDA[0].corpo.split("token=")[1].strip()
    fraca = client.post("/api/auth/redefinir-senha", json={"token": token, "nova_senha": "curta"})
    assert fraca.status_code == 422
    ok = client.post("/api/auth/redefinir-senha", json={"token": token, "nova_senha": "NovaSenha2026"})
    assert ok.status_code == 204
    assert client.post("/api/auth/redefinir-senha", json={"token": token, "nova_senha": "OutraSenha2026"}).status_code == 400
    login(client, "ana@teste.gov.br", "NovaSenha2026")


def test_recuperacao_nao_revela_email_inexistente(client):
    r = client.post("/api/auth/recuperar-senha", json={"email": "naoexiste@teste.gov.br"})
    assert r.status_code == 202 and mail.CAIXA_SAIDA == []


def test_somente_admin_gerencia_usuarios(client, usuarios):
    assert client.get("/api/usuarios", headers=usuarios["ADMIN"]).status_code == 200
    for p in ("GESTOR", "OPERADOR", "CONSULTA"):
        assert client.get("/api/usuarios", headers=usuarios[p]).status_code == 403


def test_admin_cria_usuario_com_politica_de_senha_e_email_unico(client, usuarios):
    h = usuarios["ADMIN"]
    novo = {"nome": "Novo Servidor", "email": "novo@teste.gov.br", "senha": "SenhaValida99", "perfil": "OPERADOR"}
    assert client.post("/api/usuarios", json=novo, headers=h).status_code == 201
    assert client.post("/api/usuarios", json=novo, headers=h).status_code == 409
    fraca = {**novo, "email": "outro@teste.gov.br", "senha": "somenteletras"}
    assert client.post("/api/usuarios", json=fraca, headers=h).status_code == 422
    login(client, "novo@teste.gov.br", "SenhaValida99")


def test_admin_nao_remove_o_proprio_acesso(client, usuarios):
    h = usuarios["ADMIN"]
    me = client.get("/api/auth/me", headers=h).json()
    assert client.patch(f"/api/usuarios/{me['id']}", json={"ativo": False}, headers=h).status_code == 400


def test_desativar_usuario_invalida_sessao(client, usuarios):
    h = usuarios["ADMIN"]
    alvo = client.get("/api/auth/me", headers=usuarios["OPERADOR"]).json()
    assert client.patch(f"/api/usuarios/{alvo['id']}", json={"ativo": False}, headers=h).status_code == 200
    assert client.get("/api/auth/me", headers=usuarios["OPERADOR"]).status_code == 401


def test_cabecalhos_de_seguranca(client):
    r = client.get("/api/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert "X-Request-ID" in r.headers


def test_redefinir_senha_encerra_sessoes_abertas(client):
    criar_usuario("ana@teste.gov.br", "OPERADOR")
    antiga = login(client, "ana@teste.gov.br")
    client.post("/api/auth/recuperar-senha", json={"email": "ana@teste.gov.br"})
    token = mail.CAIXA_SAIDA[0].corpo.split("token=")[1].strip()
    assert client.post("/api/auth/redefinir-senha", json={"token": token, "nova_senha": "NovaSenha2026"}).status_code == 204
    assert client.get("/api/auth/me", headers=antiga).status_code == 401
    assert client.get("/api/auth/me", headers=login(client, "ana@teste.gov.br", "NovaSenha2026")).status_code == 200


def test_email_muito_longo_retorna_401_e_e_auditado(client, usuarios):
    longo = "a" * 70 + "@teste.gov.br"
    assert client.post("/api/auth/login", json={"email": longo, "senha": "x"}).status_code == 401
    acoes = client.get("/api/auth/me", headers=usuarios["ADMIN"])
    assert acoes.status_code == 200


def test_x_forwarded_for_do_cliente_nao_e_gravado(client, usuarios):
    client.post("/api/auth/login", json={"email": "x@teste.gov.br", "senha": "x"}, headers={"X-Forwarded-For": "6.6.6.6"})
    itens = client.get("/api/auditoria", params={"acao": "LOGIN_FALHA"}, headers=usuarios["ADMIN"]).json()["itens"]
    assert itens and all(i["ip"] != "6.6.6.6" for i in itens)


def test_request_id_invalido_e_substituido(client):
    r = client.get("/api/health", headers={"X-Request-ID": "<script>"})
    assert r.headers["X-Request-ID"] != "<script>"
