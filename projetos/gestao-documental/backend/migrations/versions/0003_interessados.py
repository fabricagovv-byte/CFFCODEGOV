"""MOD-101 — cria a tabela interessados (Interessados).

Revision ID: 0003_interessados
Revises: 0002_versao_sessao
"""
import sqlalchemy as sa
from alembic import op

revision = "0003_interessados"
down_revision = "0002_versao_sessao"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "interessados",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("documento", sa.String(14), nullable=False),
        sa.Column("tipo_pessoa", sa.String(30), nullable=False),
        sa.Column("email", sa.String(254), nullable=True),
        sa.Column("telefone", sa.String(20), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_interessados_nome", "interessados", ["nome"], unique=False)
    op.create_index("ix_interessados_documento", "interessados", ["documento"], unique=True)


def downgrade() -> None:
    op.drop_table("interessados")
