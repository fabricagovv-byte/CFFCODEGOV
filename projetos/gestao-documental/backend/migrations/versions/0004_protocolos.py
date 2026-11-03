"""MOD-102 — cria a tabela protocolos (Protocolos).

Revision ID: 0004_protocolos
Revises: 0003_interessados
"""
import sqlalchemy as sa
from alembic import op

revision = "0004_protocolos"
down_revision = "0003_interessados"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "protocolos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("numero", sa.String(30), nullable=False),
        sa.Column("assunto", sa.String(200), nullable=False),
        sa.Column("interessado_id", sa.Integer(), sa.ForeignKey("interessados.id"), nullable=False),
        sa.Column("canal", sa.String(30), nullable=False),
        sa.Column("prioridade", sa.String(30), nullable=False),
        sa.Column("prazo", sa.Date(), nullable=True),
        sa.Column("valor_taxa", sa.Numeric(14, 2), nullable=True),
        sa.Column("quantidade_folhas", sa.Integer(), nullable=True),
        sa.Column("sigiloso", sa.Boolean(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_protocolos_numero", "protocolos", ["numero"], unique=True)
    op.create_index("ix_protocolos_assunto", "protocolos", ["assunto"], unique=False)
    op.create_index("ix_protocolos_interessado_id", "protocolos", ["interessado_id"], unique=False)


def downgrade() -> None:
    op.drop_table("protocolos")
