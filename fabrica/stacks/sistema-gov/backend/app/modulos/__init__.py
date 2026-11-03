"""Módulos de negócio gerados pela fábrica (um pacote por entidade: models, schemas, router).

Cada subpacote é descoberto automaticamente: os modelos entram no metadata (Alembic/testes)
e os routers são registrados na API. Não é preciso editar main.py para um módulo novo.
"""
from __future__ import annotations

import importlib
import pkgutil

from fastapi import APIRouter


def _pacotes() -> list[str]:
    return sorted(m.name for m in pkgutil.iter_modules(__path__) if m.ispkg)


def carregar_modelos() -> None:
    for nome in _pacotes():
        importlib.import_module(f"{__name__}.{nome}.models")


def routers() -> list[APIRouter]:
    carregar_modelos()
    return [importlib.import_module(f"{__name__}.{nome}.router").router for nome in _pacotes()]
