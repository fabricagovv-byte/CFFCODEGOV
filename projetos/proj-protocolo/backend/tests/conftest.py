"""Testes no PostgreSQL de TESTE do projeto (TEST_DATABASE_URL). O banco de teste é apagado."""
import os
from pathlib import Path

import pytest

URL = os.getenv("TEST_DATABASE_URL")
if not URL:
    pytest.exit("Defina TEST_DATABASE_URL com o banco PostgreSQL de TESTE do projeto", returncode=2)
os.environ["DATABASE_URL"] = URL
os.environ["GERENCIADOR_TOKEN"] = "t" * 40
BACKEND = Path(__file__).resolve().parents[1]


def alembic(*comando):
    from alembic import command
    from alembic.config import Config
    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND / "migrations"))
    getattr(command, comando[0])(cfg, *comando[1:])


@pytest.fixture(scope="session", autouse=True)
def banco():
    from sqlalchemy import text
    from app.db import motor
    with motor().begin() as c:
        c.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public"))
    alembic("upgrade", "head")


@pytest.fixture
def cliente():
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as c:
        yield c
