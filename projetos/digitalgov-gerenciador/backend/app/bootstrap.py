"""Cria o primeiro administrador do gerenciador. Só funciona com o banco sem usuários.

Uso (a senha é pedida no terminal, sem eco; não fica no histórico nem no repositório):
    python -m app.bootstrap --login admin --nome "Administrador" --perfil ADMIN
"""
from __future__ import annotations

import argparse
import getpass
import sys

from sqlalchemy import func, select

from .db import _fabrica_sessoes
from .modelos import Usuario
from .seguranca import gerar_hash_senha


class ErroBootstrap(ValueError):
    pass


def politica_senha(senha: str) -> None:
    if len(senha) < 12:
        raise ErroBootstrap("senha com menos de 12 caracteres")
    if not (any(c.isalpha() for c in senha) and any(c.isdigit() for c in senha)):
        raise ErroBootstrap("senha precisa ter letras e números")


def criar_primeiro_admin(login: str, nome: str, senha: str, perfil: str = "ADMIN") -> int:
    if perfil != "ADMIN":
        raise ErroBootstrap("o primeiro usuário precisa ser ADMIN")
    if not login.strip() or not nome.strip():
        raise ErroBootstrap("login e nome são obrigatórios")
    politica_senha(senha)
    with _fabrica_sessoes()() as s:
        if s.scalar(select(func.count()).select_from(Usuario)):
            raise ErroBootstrap("já existem usuários; use a tela de usuários (administrador) para criar outros")
        novo = Usuario(nome=nome.strip(), login=login.strip(), perfil=perfil, senha_hash=gerar_hash_senha(senha))
        s.add(novo)
        s.commit()
        return novo.id


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Cria o primeiro administrador do gerenciador.")
    p.add_argument("--login", required=True)
    p.add_argument("--nome", required=True)
    p.add_argument("--perfil", default="ADMIN")
    a = p.parse_args(argv)
    senha = getpass.getpass("Senha (mín. 12, letras e números): ")
    if senha != getpass.getpass("Repita a senha: "):
        print("ERRO: as senhas não conferem", file=sys.stderr)
        return 2
    try:
        uid = criar_primeiro_admin(a.login, a.nome, senha, a.perfil)
    except ErroBootstrap as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 2
    print(f"Administrador criado (id {uid}, login {a.login}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
