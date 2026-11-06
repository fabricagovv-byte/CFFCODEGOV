"""Converte linhas do banco em JSON."""
from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import inspect


def valor_json(v: Any) -> Any:
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime, date, time)):
        return v.isoformat()
    return v


OCULTOS = {"senha_hash", "token_hash", "caminho"}


def como_dict(obj: Any) -> dict[str, Any]:
    return {c.key: valor_json(getattr(obj, c.key)) for c in inspect(obj).mapper.column_attrs if c.key not in OCULTOS}
