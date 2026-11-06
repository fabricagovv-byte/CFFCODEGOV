"""MOD-103 — cria a tabela solicitacoes (Solicitações).

Revision ID: 0005_solicitacoes
Revises: 0004_cidadaos
"""
import sqlalchemy as sa
from alembic import op

revision = "0005_solicitacoes"
down_revision = "0004_cidadaos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "solicitacoes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("protocolo", sa.String(30), nullable=False),
        sa.Column("cidadao_id", sa.Integer(), sa.ForeignKey("cidadaos.id"), nullable=False),
        sa.Column("unidade_id", sa.Integer(), sa.ForeignKey("unidades.id"), nullable=False),
        sa.Column("canal", sa.String(30), nullable=False),
        sa.Column("assunto", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("situacao", sa.String(30), nullable=False),
        sa.Column("prazo", sa.Date(), nullable=True),
        sa.Column("prioritaria", sa.Boolean(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_solicitacoes_protocolo", "solicitacoes", ["protocolo"], unique=True)
    op.create_index("ix_solicitacoes_cidadao_id", "solicitacoes", ["cidadao_id"], unique=False)
    op.create_index("ix_solicitacoes_unidade_id", "solicitacoes", ["unidade_id"], unique=False)
    op.create_index("ix_solicitacoes_assunto", "solicitacoes", ["assunto"], unique=False)


def downgrade() -> None:
    op.drop_table("solicitacoes")
