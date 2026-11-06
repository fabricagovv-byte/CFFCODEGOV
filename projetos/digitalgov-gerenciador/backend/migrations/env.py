"""Migrações do banco central. A URL vem de GERENCIADOR_DATABASE_URL (nunca do arquivo)."""
from alembic import context
from sqlalchemy import engine_from_config, pool

from app import config as cfg
from app import modelos  # noqa: F401  (registra as tabelas)
from app.db import Base

configuracao = context.config
configuracao.set_main_option("sqlalchemy.url", cfg.carregar().database_url.replace("%", "%%"))
alvo = Base.metadata


def executar() -> None:
    motor = engine_from_config(configuracao.get_section(configuracao.config_ini_section, {}),
                               prefix="sqlalchemy.", poolclass=pool.NullPool)
    with motor.connect() as conexao:
        context.configure(connection=conexao, target_metadata=alvo, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


executar()
