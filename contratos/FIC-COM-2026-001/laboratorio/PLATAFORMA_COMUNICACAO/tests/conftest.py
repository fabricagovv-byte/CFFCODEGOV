"""Ambiente de teste: banco temporário e segredo de teste (dados DEMO)."""
import os, tempfile, pathlib
import pytest

os.environ.setdefault('DG_COMM_DB', str(pathlib.Path(tempfile.mkdtemp()) / 'comm.db'))
os.environ.setdefault('DG_COMM_SECRET', 'T' * 48)


@pytest.fixture
def client():
    """Banco zerado e migrado a cada teste."""
    from fastapi.testclient import TestClient
    from app import db
    if db.DB_PATH.exists():
        db.DB_PATH.unlink()
    from app.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture
def usuarios(client):
    """Cria usuários DEMO por perfil e devolve uma função de login."""
    from app.db import connect
    from app.security import hash_password
    from app.main import now
    with connect() as c:
        for nome, papel in (('admin', 'ADMIN'), ('editor', 'EDITOR'), ('revisor', 'APPROVER'), ('leitor', 'VIEWER')):
            c.execute('INSERT INTO users(name,username,password_hash,role,created_at) VALUES(?,?,?,?,?)',
                      (nome.title() + ' DEMO', nome, hash_password(f'senha-demo-{nome}-2026'), papel, now()))

    def login(nome):
        r = client.post('/api/login', json={'username': nome, 'password': f'senha-demo-{nome}-2026'})
        assert r.status_code == 200, r.text
        return {'Authorization': 'Bearer ' + r.json()['token']}
    return login
