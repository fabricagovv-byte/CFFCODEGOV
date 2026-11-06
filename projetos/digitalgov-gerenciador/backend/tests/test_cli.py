import os
from pathlib import Path

import pytest

from app import cli


def test_importar_profissionais_ignora_exemplos_e_cpf_completo(tmp_path, cliente, entrar):
    arq = tmp_path / "equipe.csv"
    arq.write_text("id,nome,funcao,senioridade,cpf_mascarado\n#P0,Nome Exemplo,Cargo,SENIOR,\n"
                   "P01,Jerlian,Programador,SENIOR,***.456.789-**\nP02,Ruan,Programador,SENIOR,123.456.789-00\n", encoding="utf-8")
    assert cli.importar_profissionais(arq) == 2
    h = entrar()
    pessoas = {p["nome"]: p for p in cliente.get("/api/profissionais", headers=h).json()}
    assert set(pessoas) == {"Jerlian", "Ruan"} and pessoas["Ruan"]["cpf_mascarado"] is None
    assert cli.importar_profissionais(arq) == 0                      # não duplica


def test_importar_agentes_da_fabrica(cliente, entrar):
    registro = Path(__file__).resolve().parents[4] / "fabrica" / "agentes" / "registry.yaml"
    if not registro.exists():
        pytest.skip("registro de agentes da fábrica não está neste checkout")
    assert cli.importar_agentes(registro) == 44
    agentes = cliente.get("/api/agentes", headers=entrar()).json()
    assert len(agentes) == 44 and {a["situacao"] for a in agentes} == {"INTEGRACAO_PENDENTE"}


def test_criar_projeto_a_partir_do_modelo(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "ENV_GERENCIADOR", tmp_path / "gerenciador.env")
    pasta = cli.criar_projeto("proj-teste-cli", "Projeto CLI", 8123, tmp_path, criar_banco=False, registrar=False)
    for arquivo in ("backend/app/main.py", "backend/migrations/versions/0001_inicial.py", "frontend/index.html",
                    "infra/scripts/backup.sh", ".env.example", "README.md", "docker-compose.yml"):
        assert (pasta / arquivo).exists(), arquivo
    texto = "".join(p.read_text(encoding="utf-8") for p in pasta.rglob("*") if p.is_file())
    assert "{{" not in texto and "proj_teste_cli" in (pasta / ".env.example").read_text()
    with pytest.raises(SystemExit):
        cli.criar_projeto("proj-teste-cli", "De novo", 8123, tmp_path, criar_banco=False, registrar=False)
    with pytest.raises(SystemExit):
        cli.criar_projeto("Codigo Ruim", "X", 8123, tmp_path, criar_banco=False, registrar=False)


def test_gravar_env_protege_o_arquivo(tmp_path):
    arq = tmp_path / ".env"
    cli._gravar_env(arq, {"A": "1"})
    cli._gravar_env(arq, {"A": "2", "B": "3"})
    assert arq.read_text() == "A=2\nB=3\n" and oct(os.stat(arq).st_mode & 0o777) == "0o600"


def test_criar_projeto_com_banco_isolado_no_postgresql(tmp_path, monkeypatch, cliente, entrar):
    if not os.getenv("PG_ADMIN_URL"):
        pytest.skip("PG_ADMIN_URL não definido (usuário com permissão de criar bancos)")
    import psycopg
    from sqlalchemy import create_engine
    env_ger = tmp_path / "gerenciador.env"
    monkeypatch.setattr(cli, "ENV_GERENCIADOR", env_ger)
    monkeypatch.setenv("GERENCIADOR_PROJETOS_DIR", str(tmp_path))
    try:
        pasta = cli.criar_projeto("proj-isolado-teste", "Isolado", 8124, tmp_path, criar_banco=True, registrar=True)
        env_proj = dict(l.split("=", 1) for l in (pasta / ".env").read_text().splitlines())
        url = env_proj["DATABASE_URL"].replace("+psycopg", "")
        with psycopg.connect(url) as c:
            assert c.execute("SELECT current_database()").fetchone()[0] == "proj_isolado_teste"
        with pytest.raises(psycopg.OperationalError):                       # o usuário do projeto não entra no banco central
            psycopg.connect(url.rsplit("/", 1)[0] + "/" + create_engine(os.environ["GERENCIADOR_DATABASE_URL"]).url.database)
        assert "PROJ_ISOLADO_TESTE_DATABASE_URL" in env_ger.read_text()
        projetos = cliente.get("/api/projetos", headers=entrar()).json()
        assert projetos[0]["variavel_banco"] == "PROJ_ISOLADO_TESTE_DATABASE_URL" and "senha" not in str(projetos)
        with pytest.raises(SystemExit):                                       # não recria por cima
            cli.criar_projeto("proj-isolado-teste", "De novo", 8124, tmp_path / "outra", criar_banco=True, registrar=False)
    finally:
        motor = create_engine(os.environ["PG_ADMIN_URL"], isolation_level="AUTOCOMMIT")
        with motor.connect() as c:
            for nome in ("proj_isolado_teste", "proj_isolado_teste_teste"):
                c.exec_driver_sql(f'DROP DATABASE IF EXISTS "{nome}"')
            c.exec_driver_sql('DROP ROLE IF EXISTS "proj_isolado_teste_app"')
