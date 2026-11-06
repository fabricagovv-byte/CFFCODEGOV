"""Conexão com o banco central do gerenciador (PostgreSQL em produção)."""
from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from . import config


class Base(DeclarativeBase):
    pass


@lru_cache(maxsize=1)
def motor() -> Engine:
    return create_engine(config.carregar().database_url, pool_pre_ping=True)


@lru_cache(maxsize=1)
def _fabrica_sessoes() -> sessionmaker[Session]:
    return sessionmaker(bind=motor(), expire_on_commit=False)


def sessao() -> Iterator[Session]:
    """Dependência do FastAPI: uma sessão por requisição, com commit no fim."""
    s = _fabrica_sessoes()()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()
