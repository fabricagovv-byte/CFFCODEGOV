"""MOD-001 (TR M01 — controle de sessão): sair revoga o token no servidor, limite de tentativas e auditoria de login."""


def test_sair_revoga_o_token_no_servidor(client, usuarios):
    h = usuarios('editor')
    assert client.get('/api/me', headers=h).status_code == 200
    assert client.post('/api/logout', headers=h).status_code == 200
    r = client.get('/api/me', headers=h)
    assert r.status_code == 401 and 'encerrada' in r.json()['detail']


def test_sair_encerra_somente_a_propria_sessao(client, usuarios):
    a, b = usuarios('editor'), usuarios('editor')
    client.post('/api/logout', headers=a)
    assert client.get('/api/me', headers=a).status_code == 401
    assert client.get('/api/me', headers=b).status_code == 200


def test_token_de_sessao_inexistente_e_recusado(client, usuarios):
    from app.security import token_for
    falso = token_for(1, 'sessao-que-nao-existe')
    assert client.get('/api/me', headers={'Authorization': 'Bearer ' + falso}).status_code == 401


def test_bloqueio_apos_cinco_erros_inclusive_com_senha_certa(client, usuarios):
    for i in range(5):
        assert client.post('/api/login', json={'username': 'editor', 'password': f'errada-{i}-xxxxxx'}).status_code == 401
    r = client.post('/api/login', json={'username': 'editor', 'password': 'senha-demo-editor-2026'})
    assert r.status_code == 429 and 'tentativas' in r.json()['detail']


def test_bloqueio_vale_por_usuario(client, usuarios):
    for i in range(5):
        client.post('/api/login', json={'username': 'editor', 'password': f'errada-{i}-xxxxxx'})
    assert client.post('/api/login', json={'username': 'revisor', 'password': 'senha-demo-revisor-2026'}).status_code == 200


def test_tentativas_antigas_nao_bloqueiam(client, usuarios):
    from app.db import connect
    with connect() as c:
        for _ in range(5):
            c.execute("INSERT INTO login_attempts(username,ip,success,at) VALUES('editor','testclient',0,'2020-01-01T00:00:00+00:00')")
    assert client.post('/api/login', json={'username': 'editor', 'password': 'senha-demo-editor-2026'}).status_code == 200


def test_login_ok_e_falho_ficam_na_auditoria(client, usuarios):
    usuarios('editor')
    client.post('/api/login', json={'username': 'editor', 'password': 'errada-xxxxxxxx'})
    h = usuarios('admin')
    acoes = [e['action'] for e in client.get('/api/audit', headers=h).json()]
    assert 'LOGIN_OK' in acoes and 'LOGIN_FALHOU' in acoes and 'LOGOUT' not in acoes
    client.post('/api/logout', headers=h)
    acoes = [e['action'] for e in client.get('/api/audit', headers=usuarios('admin')).json()]
    assert 'LOGOUT' in acoes


def test_auditoria_de_falha_nao_guarda_senha(client, usuarios):
    client.post('/api/login', json={'username': 'editor', 'password': 'segredo-que-nao-pode-vazar'})
    eventos = client.get('/api/audit', headers=usuarios('admin')).json()
    assert all('segredo-que-nao-pode-vazar' not in (e.get('detail') or '') for e in eventos)


def test_bloqueio_fica_registrado_na_auditoria(client, usuarios):
    for i in range(5):
        client.post('/api/login', json={'username': 'editor', 'password': f'errada-{i}-xxxxxx'})
    assert client.post('/api/login', json={'username': 'editor', 'password': 'senha-demo-editor-2026'}).status_code == 429
    acoes = [e['action'] for e in client.get('/api/audit', headers=usuarios('admin')).json()]
    assert 'LOGIN_BLOQUEADO' in acoes
