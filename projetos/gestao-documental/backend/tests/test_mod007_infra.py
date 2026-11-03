"""MOD-007 — Infraestrutura, configuração e documentação."""
from pathlib import Path

import pytest

from app.config import Config

PROJ = Path(__file__).resolve().parents[2]


def test_health_e_banco(client):
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/health/db").json()["status"] == "ok"


def test_openapi_publicado(client):
    spec = client.get("/api/openapi.json").json()
    for rota in ("/api/auth/login", "/api/documentos", "/api/pesquisa", "/api/painel/resumo", "/api/auditoria"):
        assert rota in spec["paths"]


def test_producao_exige_segredo_forte(monkeypatch):
    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.setenv("JWT_SECRET", "curto")
    with pytest.raises(RuntimeError):
        Config().validar()


@pytest.mark.parametrize("arquivo", [
    "docker-compose.yml", "docker-compose.prod.yml", ".env.example", "backend/Dockerfile", "frontend/Dockerfile",
    "infra/nginx/default.conf", "infra/nginx/prod-tls.conf", "infra/scripts/backup.sh", "infra/scripts/restore.sh",
    "docs/MANUAL_PUBLICACAO.md", "docs/MANUAL_OPERACAO.md", "docs/PLANO_CONTINUIDADE.md", "docs/SEGURANCA_LGPD.md",
    "docs/ARQUITETURA.md", "README.md"])
def test_artefatos_de_infra_e_documentacao_existem(arquivo):
    p = PROJ / arquivo
    assert p.exists() and p.stat().st_size > 100, arquivo


def test_env_example_sem_segredos_reais():
    texto = (PROJ / ".env.example").read_text()
    assert "TROQUE" in texto
