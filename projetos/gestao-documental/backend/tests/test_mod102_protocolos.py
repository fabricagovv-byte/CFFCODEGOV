"""MOD-102 — testes da API de Protocolos (gerados pela fábrica)."""

URL = "/api/protocolos"
ESCRITA = "ADMIN"
EXCLUSAO = "ADMIN"

def criar_interessados(client, h, i=3):
    corpo = {'nome': 'Nome de teste 3', 'documento': '15350946056', 'tipo_pessoa': 'JURIDICA'}
    corpo["documento"] = ['52998224725', '11144477735', '39053344705', '15350946056'][i % 4]
    r = client.post("/api/interessados", json=corpo, headers=h)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def payload(client, h, i=0, completo=False):
    corpo = dict({'numero': 'Número de teste 0', 'assunto': 'Assunto de teste 0', 'canal': 'PRESENCIAL', 'prioridade': 'NORMAL', 'prazo': '2026-01-10', 'valor_taxa': '10.50', 'quantidade_folhas': 1, 'sigiloso': True}) if completo else dict({'numero': 'Número de teste 0', 'assunto': 'Assunto de teste 0', 'canal': 'PRESENCIAL', 'prioridade': 'NORMAL'})
    corpo["numero"] = f"{i}-" + str(corpo["numero"])
    corpo["interessado_id"] = criar_interessados(client, h, i + 3)
    return corpo


def test_criar_e_detalhar(client, usuarios):
    h = usuarios[ESCRITA]
    corpo = payload(client, h, completo=True)
    r = client.post(URL, json=corpo, headers=h)
    assert r.status_code == 201, r.text
    obj = r.json()
    assert obj['ativo'] is True and obj['id'] > 0
    d = client.get(f"{URL}/{obj['id']}", headers=h).json()
    for k, v in corpo.items():
        assert str(d[k]) == str(v), k


def test_listar_paginado(client, usuarios):
    h = usuarios[ESCRITA]
    for i in range(3):
        assert client.post(URL, json=payload(client, h, i), headers=h).status_code == 201
    r = client.get(URL, params={'por_pagina': 2, 'pagina': 2}, headers=h).json()
    assert r['total'] == 3 and len(r['itens']) == 1
    assert client.get(URL, params={'por_pagina': 1000}, headers=h).status_code == 422


def test_busca_por_texto(client, usuarios):
    h = usuarios[ESCRITA]
    a = payload(client, h, 0)
    client.post(URL, json=a, headers=h)
    client.post(URL, json=payload(client, h, 1), headers=h)
    termo = str(a['numero']).split()[0]
    itens = client.get(URL, params={'q': termo}, headers=h).json()['itens']
    assert itens and all(termo.lower() in str(x['numero']).lower() for x in itens)
    assert client.get(URL, params={'q': 'inexistente-xyz'}, headers=h).json()['total'] == 0


def test_alterar(client, usuarios):
    h = usuarios[ESCRITA]
    obj = client.post(URL, json=payload(client, h), headers=h).json()
    r = client.patch(f"{URL}/{obj['id']}", json={'assunto': 'Valor alterado'}, headers=h)
    assert r.status_code == 200 and r.json()['assunto'] == 'Valor alterado'


def test_excluir_logicamente(client, usuarios):
    h = usuarios[EXCLUSAO]
    obj = client.post(URL, json=payload(client, usuarios[ESCRITA]), headers=usuarios[ESCRITA]).json()
    assert client.delete(f"{URL}/{obj['id']}", headers=h).status_code == 204
    assert client.get(URL, headers=h).json()['total'] == 0
    assert client.get(URL, params={'incluir_inativos': True}, headers=h).json()['total'] == 1
    assert client.get(f"{URL}/{obj['id']}", headers=h).json()['ativo'] is False


def test_obrigatorios(client, usuarios):
    assert client.post(URL, json={}, headers=usuarios[ESCRITA]).status_code == 422


def test_inexistente(client, usuarios):
    assert client.get(f'{URL}/999999', headers=usuarios[ESCRITA]).status_code == 404


def test_auditoria_registrada(client, usuarios):
    h = usuarios[ESCRITA]
    obj = client.post(URL, json=payload(client, h), headers=h).json()
    acoes = client.get('/api/auditoria', params={'recurso': 'protocolos'}, headers=usuarios['ADMIN']).json()['itens']
    assert any(a['acao'] == 'PROTOCOLOS_CRIADO' and a['recurso_id'] == str(obj['id']) for a in acoes)


def test_permissao_de_escrita(client, usuarios):
    assert client.post(URL, json=payload(client, usuarios[ESCRITA]), headers=usuarios['CONSULTA']).status_code == 403


def test_tamanho_maximo_numero(client, usuarios):
    h = usuarios[ESCRITA]
    corpo = payload(client, h); corpo['numero'] = 'x' * 31
    assert client.post(URL, json=corpo, headers=h).status_code == 422


def test_unico_numero(client, usuarios):
    h = usuarios[ESCRITA]
    corpo = payload(client, h)
    assert client.post(URL, json=corpo, headers=h).status_code == 201
    outro = payload(client, h, 1)
    outro['numero'] = corpo['numero']
    assert client.post(URL, json=outro, headers=h).status_code == 409


def test_tamanho_maximo_assunto(client, usuarios):
    h = usuarios[ESCRITA]
    corpo = payload(client, h); corpo['assunto'] = 'x' * 201
    assert client.post(URL, json=corpo, headers=h).status_code == 422


def test_referencia_inexistente_interessado_id(client, usuarios):
    h = usuarios[ESCRITA]
    corpo = payload(client, h); corpo['interessado_id'] = 999999
    assert client.post(URL, json=corpo, headers=h).status_code == 422


def test_enum_invalido_canal(client, usuarios):
    h = usuarios[ESCRITA]
    corpo = payload(client, h); corpo['canal'] = 'OPCAO_INEXISTENTE'
    assert client.post(URL, json=corpo, headers=h).status_code == 422


def test_enum_invalido_prioridade(client, usuarios):
    h = usuarios[ESCRITA]
    corpo = payload(client, h); corpo['prioridade'] = 'OPCAO_INEXISTENTE'
    assert client.post(URL, json=corpo, headers=h).status_code == 422
