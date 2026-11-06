"""MOD-102 — cria a tabela cidadaos (Cidadãos).

Revision ID: 0004_cidadaos
Revises: 0003_unidades
"""
import sqlalchemy as sa
from alembic import op

revision = "0004_cidadaos"
down_revision = "0003_unidades"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cidadaos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("cpf", sa.String(14), nullable=False),
        sa.Column("email", sa.String(254), nullable=True),
        sa.Column("telefone", sa.String(20), nullable=True),
        sa.Column("data_nascimento", sa.Date(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_cidadaos_nome", "cidadaos", ["nome"], unique=False)
    op.create_index("ix_cidadaos_cpf", "cidadaos", ["cpf"], unique=True)


def downgrade() -> None:
    op.drop_table("cidadaos")
