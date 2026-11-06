"""Migrações do banco do projeto. A URL vem de DATABASE_URL."""
from alembic import context
from sqlalchemy import engine_from_config, pool

from app import db, modelos  # noqa: F401

configuracao = context.config
configuracao.set_main_option("sqlalchemy.url", db.url().replace("%", "%%"))

motor = engine_from_config(configuracao.get_section(configuracao.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
with motor.connect() as conexao:
    context.configure(connection=conexao, target_metadata=db.Base.metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()
