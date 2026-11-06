"""MOD-004 (ferramenta interna): o painel da fábrica exige chave de acesso e envia cabeçalhos de segurança."""
import os
import pathlib
import tempfile

os.environ.setdefault('DG_FACTORY_DB', str(pathlib.Path(tempfile.mkdtemp()) / 'f.db'))
CHAVE = 'K' * 40

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

BASE = pathlib.Path(__file__).resolve().parents[1]


def _cli(monkeypatch, chave=CHAVE):
    if chave is None:
        monkeypatch.delenv('DG_FACTORY_TOKEN', raising=False)
    else:
        monkeypatch.setenv('DG_FACTORY_TOKEN', chave)
    return TestClient(app)


def test_api_sem_chave_configurada_fica_fechada(monkeypatch):
    with _cli(monkeypatch, None) as c:
        r = c.get('/api/overview')
        assert r.status_code == 503 and 'DG_FACTORY_TOKEN' in r.json()['detail']


def test_chave_curta_nao_abre_a_api(monkeypatch):
    with _cli(monkeypatch, 'curta') as c:
        assert c.get('/api/overview', headers={'Authorization': 'Bearer curta'}).status_code == 503


def test_api_exige_a_chave_certa(monkeypatch):
    with _cli(monkeypatch) as c:
        assert c.get('/api/team').status_code == 401
        assert c.get('/api/team', headers={'Authorization': 'Bearer ' + 'X' * 40}).status_code == 401
        assert c.post('/api/contracts/X/approve', json={'phrase': 'APROVO PLANO X'}).status_code == 401
        assert c.post('/api/contracts/X/start', json={}).status_code == 401
        assert c.get('/api/team', headers={'Authorization': 'Bearer ' + CHAVE}).status_code == 200


def test_pagina_e_saude_abrem_sem_chave(monkeypatch):
    with _cli(monkeypatch) as c:
        assert c.get('/health').status_code == 200
        assert 'Chave de acesso' in c.get('/').text


def test_cabecalhos_de_seguranca(monkeypatch):
    with _cli(monkeypatch) as c:
        for caminho in ('/', '/health', '/static/painel.js'):
            h = c.get(caminho).headers
            assert "default-src 'self'" in h['content-security-policy'] and h['x-frame-options'] == 'DENY', caminho
            assert h['x-content-type-options'] == 'nosniff'


def test_pagina_sem_script_nem_estilo_embutido():
    html = (BASE / 'static' / 'index.html').read_text(encoding='utf-8')
    assert '<script>' not in html and '<style>' not in html and 'style="' not in html
    assert '/static/painel.js' in html and '/static/painel.css' in html


def test_painel_envia_a_chave_nas_chamadas():
    js = (BASE / 'static' / 'painel.js').read_text(encoding='utf-8')
    assert "'Authorization'" in js and 'sessionStorage' in js


def test_dependencias_com_versao_fixa():
    linhas = [l.strip() for l in (BASE / 'requirements.txt').read_text().splitlines() if l.strip() and not l.startswith('#')]
    assert linhas and all('==' in l for l in linhas), linhas
