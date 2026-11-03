"""Fixtures. Por padrão usa SQLite temporário; defina TEST_DATABASE_URL para rodar em PostgreSQL real
(as migrações Alembic são aplicadas e o trigger de auditoria é testado)."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp(prefix="gd-test-"))
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL") or f"sqlite:///{_tmp / 'test.db'}"
os.environ["UPLOAD_DIR"] = str(_tmp / "uploads")
os.environ["MAX_UPLOAD_MB"] = "1"
os.environ["BCRYPT_ROUNDS"] = "4"  # custo baixo só nos testes (produção: 12)
os.environ.setdefault("JWT_SECRET", "segredo-de-teste-apenas-para-pytest-0123456789")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app import mail  # noqa: E402
from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Usuario  # noqa: E402
from app.security import hash_senha, limitador  # noqa: E402

SENHA = "SenhaForte123"
EH_PG = engine.dialect.name == "postgresql"
TABELAS = ["auditoria", "arquivos", "documentos", "tokens_revogados", "tokens_recuperacao", "usuarios"]


@pytest.fixture(scope="session", autouse=True)
def _schema():
    if EH_PG:
        raiz = Path(__file__).resolve().parents[1]
        with engine.begin() as c:
            c.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public"))
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=raiz, check=True,
                       env={**os.environ, "DATABASE_URL": os.environ["DATABASE_URL"]})
    else:
        Base.metadata.create_all(engine)
    yield


@pytest.fixture(autouse=True)
def _limpar():
    with engine.begin() as c:
        if EH_PG:
            c.execute(text(f"TRUNCATE {', '.join(TABELAS)} RESTART IDENTITY CASCADE"))
        else:
            for t in TABELAS:
                c.execute(text(f"DELETE FROM {t}"))
    limitador.limpar()
    mail.CAIXA_SAIDA.clear()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def criar_usuario(email: str, perfil: str, ativo: bool = True) -> Usuario:
    with SessionLocal() as db:
        u = Usuario(nome=f"Usuário {perfil.title()}", email=email, senha_hash=hash_senha(SENHA), perfil=perfil,
                    ativo=ativo)
        db.add(u)
        db.commit()
        return u


def login(client: TestClient, email: str, senha: str = SENHA) -> dict:
    r = client.post("/api/auth/login", json={"email": email, "senha": senha})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def usuarios(client):
    """Cria um usuário de cada perfil e devolve cabeçalhos autenticados."""
    hdr = {}
    for perfil in ("ADMIN", "GESTOR", "OPERADOR", "CONSULTA"):
        email = f"{perfil.lower()}@teste.gov.br"
        criar_usuario(email, perfil)
        hdr[perfil] = login(client, email)
    return hdr


PDF_MINIMO = (b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\n"
              b"trailer<</Root 1 0 R>>\n%%EOF\n")


def criar_doc(client, hdr, **kw) -> dict:
    dados = {"titulo": "Ofício de teste", "tipo": "Ofício", "assunto": "Assunto fictício",
             "interessado": "Secretaria Fictícia", "classificacao": "PUBLICO", **kw}
    r = client.post("/api/documentos", json=dados, headers=hdr)
    assert r.status_code == 201, r.text
    return r.json()
