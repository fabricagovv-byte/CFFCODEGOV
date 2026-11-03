from alembic import context
from sqlalchemy import engine_from_config, pool

from app import models  # noqa: F401  (registra tabelas)
from app.config import config as app_config
from app.db import Base

cfg = context.config
cfg.set_main_option("sqlalchemy.url", app_config.database_url.replace("%", "%%"))
target_metadata = Base.metadata


def run_offline() -> None:
    context.configure(url=app_config.database_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_online() -> None:
    eng = engine_from_config(cfg.get_section(cfg.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with eng.connect() as conn:
        context.configure(connection=conn, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_offline()
else:
    run_online()
