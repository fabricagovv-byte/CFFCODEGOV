"""Linha de comando do gerenciador: administrador, importações e criação de projetos isolados.

Exemplos:
  python -m app.cli criar-admin --nome "Warley" --login warley
  python -m app.cli importar-profissionais ../../contratos/FIC-COM-2026-001/PROFISSIONAIS.csv
  python -m app.cli importar-agentes ../../fabrica/agentes/registry.yaml
  python -m app.cli projeto criar --codigo proj-exemplo --nome "Exemplo" --porta 8100 --criar-banco --registrar
"""
from __future__ import annotations

import argparse
import csv
import getpass
import os
import re
import secrets
import shutil
import sys
from pathlib import Path

from sqlalchemy import create_engine, select, text

from . import config
from .config import RAIZ_PROJETO
from .db import _fabrica_sessoes
from .modelos import Agente, Profissional, Projeto, Usuario
from .seguranca import gerar_hash_senha

MODELO = RAIZ_PROJETO / "modelo_projeto"
ENV_GERENCIADOR = Path(os.getenv("GERENCIADOR_ENV", str(RAIZ_PROJETO / ".env")))


def criar_admin(nome: str, login: str) -> None:
    senha = os.getenv("GERENCIADOR_SENHA_ADMIN") or getpass.getpass("Senha do administrador (12+ caracteres): ")
    with _fabrica_sessoes()() as s:
        if s.scalar(select(Usuario).where(Usuario.login == login)):
            sys.exit(f"Já existe o usuário {login}")
        s.add(Usuario(nome=nome, login=login, perfil="ADMIN", senha_hash=gerar_hash_senha(senha)))
        s.commit()
    print(f"Administrador {login} criado.")


def importar_profissionais(arquivo: Path) -> int:
    """CSV com colunas nome e funcao (ou cargo). Linhas começadas por # são ignoradas. Não importa CPF completo."""
    n = 0
    with open(arquivo, encoding="utf-8-sig") as f, _fabrica_sessoes()() as s:
        for linha in csv.DictReader(f):
            nome = (linha.get("nome") or "").strip()
            cargo = (linha.get("funcao") or linha.get("cargo") or "").strip()
            if not nome or nome.startswith("#") or (linha.get("id") or "").startswith("#") or not cargo:
                continue
            if s.scalar(select(Profissional).where(Profissional.nome == nome)):
                continue
            cpf = (linha.get("cpf_mascarado") or "").strip()
            s.add(Profissional(nome=nome, cargo=cargo, perfil=(linha.get("senioridade") or "").strip() or None,
                               cpf_mascarado=cpf if re.fullmatch(r"\*{3}\.\d{3}\.\d{3}-\*{2}", cpf) else None))
            n += 1
        s.commit()
    print(f"{n} profissional(is) importado(s).")
    return n


def importar_agentes(arquivo: Path) -> int:
    import yaml
    dados = yaml.safe_load(arquivo.read_text(encoding="utf-8"))
    n = 0
    with _fabrica_sessoes()() as s:
        for a in dados.get("agentes", dados):
            if s.scalar(select(Agente).where(Agente.codigo == a["id"])):
                continue
            s.add(Agente(codigo=a["id"], nome=a["nome"], funcao=a.get("funcao"), situacao="INTEGRACAO_PENDENTE"))
            n += 1
        s.commit()
    print(f"{n} agente(s) importado(s), todos com integração pendente.")
    return n


def _gravar_env(arquivo: Path, valores: dict[str, str]) -> None:
    """Acrescenta ou troca variáveis num .env, com permissão só do dono (a senha não aparece na tela)."""
    linhas = arquivo.read_text(encoding="utf-8").splitlines() if arquivo.exists() else []
    linhas = [l for l in linhas if l.split("=", 1)[0] not in valores]
    linhas += [f"{k}={v}" for k, v in valores.items()]
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    os.chmod(arquivo, 0o600)


def _criar_banco(banco: str, usuario: str) -> str:
    """Cria usuário e banco próprios (e o banco de teste) usando PG_ADMIN_URL. Devolve a senha gerada.

    Se algo falhar no meio, desfaz o que criou. Mensagens de erro nunca mostram a senha."""
    from sqlalchemy.exc import SQLAlchemyError

    admin = os.getenv("PG_ADMIN_URL")
    if not admin:
        sys.exit("Defina PG_ADMIN_URL (usuário do PostgreSQL com permissão de criar bancos). Veja docs/MANUAL_BANCO_DE_DADOS.md")
    senha = secrets.token_urlsafe(24)
    if not re.fullmatch(r"[A-Za-z0-9_-]+", senha):  # garante que a senha pode ir entre aspas no comando
        sys.exit("Falha ao gerar a senha do banco")
    motor = create_engine(admin, isolation_level="AUTOCOMMIT")
    criados: list[str] = []
    try:
        with motor.connect() as c:
            if c.execute(text("SELECT 1 FROM pg_roles WHERE rolname = :u"), {"u": usuario}).scalar():
                sys.exit(f"O usuário de banco {usuario} já existe: escolha outro código ou remova-o antes")
            c.exec_driver_sql(f"CREATE ROLE \"{usuario}\" LOGIN PASSWORD '{senha}'")
            criados.append(f'ROLE "{usuario}"')
            c.exec_driver_sql(f'GRANT "{usuario}" TO CURRENT_USER')
            for nome in (banco, f"{banco}_teste"):
                c.exec_driver_sql(f'CREATE DATABASE "{nome}" OWNER "{usuario}"')
                criados.insert(0, f'DATABASE "{nome}"')
                c.exec_driver_sql(f'REVOKE CONNECT ON DATABASE "{nome}" FROM PUBLIC')
    except SQLAlchemyError as erro:
        with motor.connect() as c:
            for objeto in criados:
                c.exec_driver_sql(f"DROP {objeto}")
        motivo = type(getattr(erro, "orig", erro)).__name__
        sys.exit(f"Não foi possível criar o banco ({motivo}). Nada ficou criado. Confira PG_ADMIN_URL e as permissões do usuário")
    finally:
        motor.dispose()
    return senha


def criar_projeto(codigo: str, nome: str, porta: int, destino: Path, criar_banco: bool, registrar: bool) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,59}", codigo):
        sys.exit("Código inválido: use letras minúsculas, números e hífen (ex.: proj-protocolo)")
    pasta = destino / codigo
    if pasta.exists():
        sys.exit(f"A pasta {pasta} já existe")
    base = codigo.replace("-", "_")
    variavel = base.upper()
    trocas = {"{{CODIGO}}": codigo, "{{NOME}}": nome, "{{BANCO}}": base, "{{USUARIO_BANCO}}": f"{base}_app",
              "{{VAR_BANCO}}": f"{variavel}_DATABASE_URL", "{{VAR_TOKEN}}": f"{variavel}_TOKEN", "{{PORTA}}": str(porta)}
    senha = _criar_banco(base, f"{base}_app") if criar_banco else None
    shutil.copytree(MODELO, pasta, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    for arquivo in pasta.rglob("*"):
        if arquivo.is_file() and arquivo.suffix in {".py", ".md", ".html", ".js", ".css", ".yml", ".sh", ".example", ".ini", ""}:
            conteudo = arquivo.read_text(encoding="utf-8")
            for de, para in trocas.items():
                conteudo = conteudo.replace(de, para)
            arquivo.write_text(conteudo, encoding="utf-8")
    print(f"Projeto criado em {pasta}")

    token = secrets.token_urlsafe(32)
    if senha:
        host = create_engine(os.environ["PG_ADMIN_URL"]).url
        url = f"postgresql+psycopg://{base}_app:{senha}@{host.host}:{host.port or 5432}/{base}"
        _gravar_env(pasta / ".env", {"DATABASE_URL": url, "TEST_DATABASE_URL": url.rsplit("/", 1)[0] + f"/{base}_teste",
                                     "GERENCIADOR_TOKEN": token, "PORTA": str(porta)})
        _gravar_env(ENV_GERENCIADOR, {f"{variavel}_DATABASE_URL": url, f"{variavel}_TOKEN": token})
        print(f"Banco {base} e usuário {base}_app criados. Senha gravada em {pasta / '.env'} e em {ENV_GERENCIADOR} (não é exibida).")
    if registrar:
        with _fabrica_sessoes()() as s:
            s.add(Projeto(codigo=codigo, nome=nome, pasta=os.path.relpath(pasta, config.carregar().pasta_projetos),
                          url_servico=f"http://127.0.0.1:{porta}", variavel_banco=f"{variavel}_DATABASE_URL",
                          variavel_token=f"{variavel}_TOKEN"))
            s.commit()
        print(f"Projeto {codigo} registrado no gerenciador (variáveis {variavel}_DATABASE_URL e {variavel}_TOKEN).")
    return pasta


def main() -> None:
    p = argparse.ArgumentParser(description="Gerenciador Central DigitalGov")
    sub = p.add_subparsers(dest="comando", required=True)
    a = sub.add_parser("criar-admin"); a.add_argument("--nome", required=True); a.add_argument("--login", required=True)
    a = sub.add_parser("importar-profissionais"); a.add_argument("arquivo", type=Path)
    a = sub.add_parser("importar-agentes"); a.add_argument("arquivo", type=Path)
    pj = sub.add_parser("projeto").add_subparsers(dest="acao", required=True)
    a = pj.add_parser("criar")
    a.add_argument("--codigo", required=True); a.add_argument("--nome", required=True)
    a.add_argument("--porta", type=int, default=8100)
    a.add_argument("--destino", type=Path, default=None, help="pasta onde criar (padrão: GERENCIADOR_PROJETOS_DIR)")
    a.add_argument("--criar-banco", action="store_true"); a.add_argument("--registrar", action="store_true")
    args = p.parse_args()
    if args.comando == "criar-admin":
        criar_admin(args.nome, args.login)
    elif args.comando == "importar-profissionais":
        importar_profissionais(args.arquivo)
    elif args.comando == "importar-agentes":
        importar_agentes(args.arquivo)
    else:
        criar_projeto(args.codigo, args.nome, args.porta, args.destino or config.carregar().pasta_projetos, args.criar_banco, args.registrar)


if __name__ == "__main__":
    main()
