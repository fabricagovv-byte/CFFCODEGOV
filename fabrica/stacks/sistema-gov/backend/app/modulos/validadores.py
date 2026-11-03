"""Validadores compartilhados pelos módulos gerados."""
from __future__ import annotations

import re


def so_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")


def cpf_valido(c: str) -> bool:
    if len(c) != 11 or c == c[0] * 11:
        return False
    for n in (9, 10):
        dv = (sum(int(c[i]) * (n + 1 - i) for i in range(n)) * 10) % 11 % 10
        if dv != int(c[n]):
            return False
    return True


def cnpj_valido(c: str) -> bool:
    if len(c) != 14 or c == c[0] * 14:
        return False
    for n in (12, 13):
        pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2] if n == 12 else [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        resto = sum(int(c[i]) * pesos[i] for i in range(n)) % 11
        dv = 0 if resto < 2 else 11 - resto
        if dv != int(c[n]):
            return False
    return True


def validar_cpf_cnpj(valor: str) -> str:
    d = so_digitos(valor)
    if not (cpf_valido(d) or cnpj_valido(d)):
        raise ValueError("CPF/CNPJ inválido")
    return d
