"""MOD-002 (correções): estados visíveis por perfil, validações, CSV seguro e privacidade dos chamados."""


def _post_em_cada_estado(client, ed, rv):
    ch = client.post('/api/channels', headers=ed, json={'name': 'Canal DEMO'}).json()['id']
    ids = {}
    for estado in ('RASCUNHO', 'EM_REVISAO', 'PUBLICADO'):
        pid = client.post('/api/posts', headers=ed, json={'channel_id': ch, 'title': f'Post {estado}', 'body': 'Conteúdo de teste DEMO'}).json()['id']
        if estado != 'RASCUNHO':
            client.post(f'/api/posts/{pid}/submit', headers=ed)
        if estado == 'PUBLICADO':
            client.post(f'/api/posts/{pid}/approve', headers=rv)
            client.post(f'/api/posts/{pid}/publish', headers=rv)
        ids[estado] = pid
    return ids


def test_leitor_ve_somente_publicadas(client, usuarios):
    ed, rv, lv = usuarios('editor'), usuarios('revisor'), usuarios('leitor')
    _post_em_cada_estado(client, ed, rv)
    assert {p['status'] for p in client.get('/api/posts', headers=lv).json()} == {'PUBLICADO'}
    assert {p['status'] for p in client.get('/api/posts', headers=ed).json()} == {'RASCUNHO', 'EM_REVISAO', 'PUBLICADO'}


def test_painel_do_leitor_conta_somente_publicadas(client, usuarios):
    ed, rv, lv = usuarios('editor'), usuarios('revisor'), usuarios('leitor')
    _post_em_cada_estado(client, ed, rv)
    assert client.get('/api/overview', headers=lv).json()['kpis']['posts'] == 1
    assert client.get('/api/overview', headers=ed).json()['kpis']['posts'] == 3


def test_chamado_com_contato_inexistente_responde_404(client, usuarios):
    r = client.post('/api/tickets', headers=usuarios('editor'), json={'subject': 'Assunto DEMO', 'description': 'Descrição DEMO', 'contact_id': 9999})
    assert r.status_code == 404 and 'Contato' in r.json()['detail']


def test_campanha_com_canal_inexistente_responde_404(client, usuarios):
    r = client.post('/api/campaigns', headers=usuarios('editor'), json={'name': 'Camp DEMO', 'objective': 'Objetivo', 'channel_id': 9999})
    assert r.status_code == 404 and 'Canal' in r.json()['detail']


def test_campanha_com_canal_valido(client, usuarios):
    ed = usuarios('editor')
    ch = client.post('/api/channels', headers=ed, json={'name': 'Canal DEMO'}).json()['id']
    assert client.post('/api/campaigns', headers=ed, json={'name': 'Camp DEMO', 'objective': 'Objetivo', 'channel_id': ch}).status_code == 201


def test_email_invalido_e_recusado(client, usuarios):
    ed = usuarios('editor')
    for ruim in ('isto-nao-e-email', 'a@b', 'a b@c.com', '@dominio.com'):
        assert client.post('/api/contacts', headers=ed, json={'name': 'Fulano', 'email': ruim}).status_code == 422, ruim
    assert client.post('/api/contacts', headers=ed, json={'name': 'Fulano', 'email': 'fulano@exemplo.gov.br'}).status_code == 201
    assert client.post('/api/contacts', headers=ed, json={'name': 'Sem e-mail'}).status_code == 201


def test_csv_neutraliza_formulas(client, usuarios):
    ed = usuarios('editor')
    for assunto in ('=HYPERLINK("http://x")', '+SOMA(1)', '-2+3 teste', '@cmd teste'):
        client.post('/api/tickets', headers=ed, json={'subject': assunto, 'description': 'Descrição DEMO'})
    import csv, io
    texto = client.get('/api/export/tickets.csv', headers=usuarios('revisor')).text.lstrip('\ufeff')
    assuntos = [linha[1] for linha in list(csv.reader(io.StringIO(texto)))[1:]]
    assert len(assuntos) == 4
    assert all(a.startswith("'") for a in assuntos), assuntos


def test_leitor_nao_ve_descricao_nem_contato_dos_chamados(client, usuarios):
    ed = usuarios('editor')
    cid = client.post('/api/contacts', headers=ed, json={'name': 'Pessoa DEMO'}).json()['id']
    client.post('/api/tickets', headers=ed, json={'subject': 'Assunto DEMO', 'description': 'Dado pessoal DEMO', 'contact_id': cid})
    item = client.get('/api/tickets', headers=usuarios('leitor')).json()[0]
    assert 'description' not in item and 'contact_id' not in item and item['subject'] == 'Assunto DEMO'
    completo = client.get('/api/tickets', headers=ed).json()[0]
    assert completo['description'] == 'Dado pessoal DEMO'
