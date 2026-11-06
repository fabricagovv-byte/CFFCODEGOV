"""tabelas iniciais do projeto

Revisão: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "registros",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "ciclos_producao",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("iniciado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("origem", sa.String(60), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("ciclos_producao")
    op.drop_table("registros")
