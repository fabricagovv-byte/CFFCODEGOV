"""Versão de sessão no usuário: trocar a senha encerra sessões abertas.

Revision ID: 0002_versao_sessao
Revises: 0001_inicial
Create Date: 2026-11-03
"""
import sqlalchemy as sa
from alembic import op

revision = "0002_versao_sessao"
down_revision = "0001_inicial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("versao_sessao", sa.Integer, nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("usuarios", "versao_sessao")
