"""MOD-101 — cria a tabela unidades (Unidades).

Revision ID: 0003_unidades
Revises: 0002_versao_sessao
"""
import sqlalchemy as sa
from alembic import op

revision = "0003_unidades"
down_revision = "0002_versao_sessao"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "unidades",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("sigla", sa.String(20), nullable=False),
        sa.Column("municipio", sa.String(100), nullable=False),
        sa.Column("telefone", sa.String(20), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_unidades_nome", "unidades", ["nome"], unique=False)
    op.create_index("ix_unidades_sigla", "unidades", ["sigla"], unique=True)


def downgrade() -> None:
    op.drop_table("unidades")
