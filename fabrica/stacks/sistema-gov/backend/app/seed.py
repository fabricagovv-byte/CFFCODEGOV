"""Carga inicial. Uso: python -m app.seed  (variáveis ADMIN_EMAIL, ADMIN_SENHA; DEMO=1 para dados fictícios)."""
from __future__ import annotations

import os
import sys

from sqlalchemy import select

from .config import config
from .db import SessionLocal
from .models import Documento, Usuario
from .security import hash_senha, validar_politica_senha

DEMO_USUARIOS = [  # dados FICTÍCIOS para preview local
    ("Gestora Demonstração", "gestor@demo.gov.br", "GESTOR"),
    ("Operador Demonstração", "operador@demo.gov.br", "OPERADOR"),
    ("Consulta Demonstração", "consulta@demo.gov.br", "CONSULTA"),
]
DEMO_DOCS = [
    ("Ofício de solicitação de manutenção predial", "Ofício", "Solicitação de reparo no telhado da escola municipal", "Secretaria de Educação", "PUBLICO"),
    ("Portaria de nomeação de comissão", "Portaria", "Nomeia comissão de recebimento de bens", "Gabinete", "PUBLICO"),
    ("Memorando sobre férias coletivas", "Memorando", "Organização das férias da equipe de TI", "Departamento de TI", "RESTRITO"),
    ("Contrato de fornecimento de merenda", "Contrato", "Fornecimento de gêneros alimentícios", "Empresa Fictícia Ltda", "PUBLICO"),
    ("Parecer jurídico sobre licitação", "Parecer", "Análise de recurso administrativo", "Procuradoria", "SIGILOSO"),
]


def main() -> int:
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    senha = os.getenv("ADMIN_SENHA", "")
    if not email or validar_politica_senha(senha):
        print("Defina ADMIN_EMAIL e ADMIN_SENHA (>=10 caracteres, letras e números).", file=sys.stderr)
        return 1
    demo = os.getenv("DEMO") == "1"
    if demo and config.env == "prod":
        print("DEMO=1 não é permitido em produção.", file=sys.stderr)
        return 1
    with SessionLocal() as db:
        admin = db.scalar(select(Usuario).where(Usuario.email == email))
        if not admin:
            admin = Usuario(nome="Administrador", email=email, senha_hash=hash_senha(senha), perfil="ADMIN")
            db.add(admin)
            db.flush()
            print(f"admin criado: {email}")
        if demo:
            senha_demo = os.getenv("DEMO_SENHA", senha)
            for nome, em, perfil in DEMO_USUARIOS:
                if not db.scalar(select(Usuario).where(Usuario.email == em)):
                    db.add(Usuario(nome=nome, email=em, senha_hash=hash_senha(senha_demo), perfil=perfil))
            if not db.scalar(select(Documento.id).limit(1)):
                for i, (titulo, tipo, assunto, interessado, cls) in enumerate(DEMO_DOCS, start=1):
                    db.add(Documento(numero=f"DEMO/{i:06d}", titulo=titulo, tipo=tipo, assunto=assunto,
                                     interessado=interessado, classificacao=cls, criado_por_id=admin.id))
            print("dados fictícios de demonstração carregados")
        db.commit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
