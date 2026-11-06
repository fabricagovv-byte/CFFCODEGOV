"""Linha de comando: banco, migrações e usuários."""
from __future__ import annotations

import argparse
import sqlite3

from . import migrations
from .comum import now
from .db import DB_PATH, connect, init
from .security import hash_password

PERFIS = ("ADMIN", "EDITOR", "APPROVER", "VIEWER")


def main() -> None:
    parser = argparse.ArgumentParser(description="Administração da plataforma de comunicação")
    parser.add_argument("command", choices=["init", "add-user", "migrations", "rollback"])
    parser.add_argument("--name", default="Administrador")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password")
    parser.add_argument("--role", default="ADMIN", choices=PERFIS)
    parser.add_argument("--to", type=int, help="rollback: versão de destino")
    args = parser.parse_args()

    if args.command == "rollback":
        if args.to is None:
            parser.error("Informe --to (versão de destino)")
        print("Migrações desfeitas:", migrations.rollback(DB_PATH, args.to) or "nenhuma")
        return
    if args.command == "migrations":
        print(migrations.status(DB_PATH))
        return

    init()
    if args.command == "init":
        print("Banco de dados criado/atualizado (migrações:", migrations.status(DB_PATH)["atual"], ") sem usuários ou conteúdo")
        return

    if not args.password:
        parser.error("Informe --password (não compartilhe em repositórios)")
    try:
        with connect() as c:
            c.execute(
                "INSERT INTO users (name, username, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
                (args.name, args.username, hash_password(args.password), args.role, now()),
            )
    except sqlite3.IntegrityError:
        parser.error("Usuário já existe")
    print("Usuário criado:", args.username, args.role)


if __name__ == "__main__":
    main()
