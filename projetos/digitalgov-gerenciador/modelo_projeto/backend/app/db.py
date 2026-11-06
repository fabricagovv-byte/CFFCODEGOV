"""Banco próprio do projeto. A conexão vem de DATABASE_URL (arquivo .env, nunca do código)."""
from __future__ import annotations

import os
from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def url() -> str:
    valor = os.getenv("DATABASE_URL", "")
    if not valor:
        raise RuntimeError("Defina DATABASE_URL no arquivo .env do projeto (veja docs/BANCO_DE_DADOS.md)")
    return valor


@lru_cache(maxsize=1)
def motor() -> Engine:
    return create_engine(url(), pool_pre_ping=True)


def sessao() -> Iterator[Session]:
    s = sessionmaker(bind=motor(), expire_on_commit=False)()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()
