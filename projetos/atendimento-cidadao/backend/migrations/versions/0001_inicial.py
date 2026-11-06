"""Estrutura inicial: usuários, tokens, documentos, arquivos e auditoria.

Revision ID: 0001_inicial
Revises:
Create Date: 2026-11-03
"""
import sqlalchemy as sa
from alembic import op

revision = "0001_inicial"
down_revision = None
branch_labels = None
depends_on = None

TZ = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("senha_hash", sa.String(100), nullable=False),
        sa.Column("perfil", sa.String(20), nullable=False),
        sa.Column("ativo", sa.Boolean, nullable=False),
        sa.Column("criado_em", TZ, nullable=False),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)

    op.create_table(
        "tokens_recuperacao",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expira_em", TZ, nullable=False),
        sa.Column("usado", sa.Boolean, nullable=False),
    )
    op.create_index("ix_tokens_recuperacao_usuario_id", "tokens_recuperacao", ["usuario_id"])

    op.create_table(
        "tokens_revogados",
        sa.Column("jti", sa.String(64), primary_key=True),
        sa.Column("expira_em", TZ, nullable=False),
    )
    op.create_index("ix_tokens_revogados_expira_em", "tokens_revogados", ["expira_em"])

    op.create_table(
        "documentos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("numero", sa.String(40), nullable=False),
        sa.Column("titulo", sa.String(300), nullable=False),
        sa.Column("tipo", sa.String(60), nullable=False),
        sa.Column("assunto", sa.Text, nullable=False),
        sa.Column("interessado", sa.String(200), nullable=False),
        sa.Column("classificacao", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("criado_por_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("criado_em", TZ, nullable=False),
        sa.Column("atualizado_em", TZ, nullable=False),
    )
    op.create_index("ix_documentos_numero", "documentos", ["numero"], unique=True)
    op.create_index("ix_documentos_tipo", "documentos", ["tipo"])
    op.create_index("ix_documentos_classificacao", "documentos", ["classificacao"])
    op.create_index("ix_documentos_status", "documentos", ["status"])
    op.create_index("ix_documentos_criado_em", "documentos", ["criado_em"])

    op.create_table(
        "arquivos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("documento_id", sa.Integer, sa.ForeignKey("documentos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome_original", sa.String(255), nullable=False),
        sa.Column("caminho", sa.String(500), nullable=False),
        sa.Column("tamanho", sa.BigInteger, nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("enviado_por_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("enviado_em", TZ, nullable=False),
    )
    op.create_index("ix_arquivos_documento_id", "arquivos", ["documento_id"])
    op.create_index("ix_arquivos_sha256", "arquivos", ["sha256"])

    op.create_table(
        "auditoria",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("momento", TZ, nullable=False),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column("acao", sa.String(60), nullable=False),
        sa.Column("recurso", sa.String(60), nullable=False),
        sa.Column("recurso_id", sa.String(60), nullable=False),
        sa.Column("ip", sa.String(45), nullable=False),
        sa.Column("detalhes", sa.Text, nullable=False),
    )
    op.create_index("ix_auditoria_momento", "auditoria", ["momento"])
    op.create_index("ix_auditoria_usuario_id", "auditoria", ["usuario_id"])
    op.create_index("ix_auditoria_acao", "auditoria", ["acao"])
    op.create_index("ix_auditoria_recurso", "auditoria", ["recurso", "recurso_id"])

    if op.get_bind().dialect.name == "postgresql":
        # Trilha de auditoria imutável: bloqueia UPDATE e DELETE.
        op.execute("""
            CREATE OR REPLACE FUNCTION auditoria_somente_insercao() RETURNS trigger AS $$
            BEGIN
              RAISE EXCEPTION 'auditoria é somente inserção (operação % bloqueada)', TG_OP;
            END; $$ LANGUAGE plpgsql;
        """)
        op.execute("""
            CREATE TRIGGER trg_auditoria_imutavel BEFORE UPDATE OR DELETE ON auditoria
            FOR EACH ROW EXECUTE FUNCTION auditoria_somente_insercao();
        """)


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP TRIGGER IF EXISTS trg_auditoria_imutavel ON auditoria")
        op.execute("DROP FUNCTION IF EXISTS auditoria_somente_insercao()")
    for t in ("auditoria", "arquivos", "documentos", "tokens_revogados", "tokens_recuperacao", "usuarios"):
        op.drop_table(t)
