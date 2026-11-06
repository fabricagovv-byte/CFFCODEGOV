"""Testes no PostgreSQL real: banco de teste próprio (TEST_DATABASE_URL), limpo antes de cada teste."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

URL = os.getenv("TEST_DATABASE_URL")
if not URL:
    pytest.exit("Defina TEST_DATABASE_URL apontando para um banco PostgreSQL de TESTE (ele é apagado nos testes)", returncode=2)
os.environ["GERENCIADOR_DATABASE_URL"] = URL
os.environ["GERENCIADOR_ARQUIVOS"] = tempfile.mkdtemp(prefix="arquivos-")
os.environ.setdefault("GERENCIADOR_MAX_UPLOAD_MB", "1")

BACKEND = Path(__file__).resolve().parents[1]


def _alembic(*comando: str) -> None:
    from alembic import command
    from alembic.config import Config
    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND / "migrations"))
    getattr(command, comando[0])(cfg, *comando[1:])


@pytest.fixture(scope="session", autouse=True)
def banco_migrado():
    from sqlalchemy import text
    from app.db import motor
    with motor().begin() as c:
        c.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public"))
    _alembic("upgrade", "head")
    yield


@pytest.fixture(autouse=True)
def banco_limpo():
    from sqlalchemy import text
    from app.db import Base, motor
    tabelas = ", ".join(t.name for t in Base.metadata.sorted_tables)
    with motor().begin() as c:
        c.execute(text(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
def cliente():
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as c:
        yield c


def criar_usuario(login: str, perfil: str, senha: str = "senha-de-teste-123") -> None:
    from app.db import _fabrica_sessoes
    from app.modelos import Usuario
    from app.seguranca import gerar_hash_senha
    with _fabrica_sessoes()() as s:
        s.add(Usuario(nome=login.title(), login=login, perfil=perfil, senha_hash=gerar_hash_senha(senha)))
        s.commit()


@pytest.fixture
def entrar(cliente):
    def _entrar(login: str = "admin", perfil: str = "ADMIN") -> dict:
        criar_usuario(login, perfil)
        r = cliente.post("/api/login", json={"login": login, "senha": "senha-de-teste-123"})
        assert r.status_code == 200, r.text
        return {"Authorization": "Bearer " + r.json()["token"]}
    return _entrar


@pytest.fixture
def base(cliente, entrar):
    """Órgão, contrato, OS autorizada e projeto prontos para os testes."""
    h = entrar()
    org = cliente.post("/api/orgaos", headers=h, json={"nome": "Prefeitura de Teste", "sigla": "PMT", "esfera": "MUNICIPAL"}).json()
    ct = cliente.post("/api/contratos", headers=h, json={"orgao_id": org["id"], "numero": "12/2026", "objeto": "Sistema de teste",
                                                          "metrica": "UST", "quantidade_contratada": 1000, "valor_unitario": 30,
                                                          "vigencia_inicio": "2026-01-01", "vigencia_fim": "2099-12-31"}).json()
    os_ = cliente.post("/api/ordens-servico", headers=h, json={"contrato_id": ct["id"], "numero": "OS-1", "descricao": "Primeira OS",
                                                              "quantidade": 300, "autorizada": True, "autorizado_por": "Fiscal Teste",
                                                              "autorizado_em": "2026-11-01"}).json()
    pj = cliente.post("/api/projetos", headers=h, json={"codigo": "proj-teste", "nome": "Projeto Teste", "contrato_id": ct["id"],
                                                        "os_id": os_["id"]}).json()
    return {"h": h, "orgao": org, "contrato": ct, "os": os_, "projeto": pj}
