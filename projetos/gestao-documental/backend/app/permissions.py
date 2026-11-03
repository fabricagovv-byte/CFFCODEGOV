"""Perfis e permissões (menor privilégio)."""
from __future__ import annotations

PERMISSOES: dict[str, set[str]] = {
    "ADMIN": {"doc:ler", "doc:criar", "doc:editar", "doc:arquivar", "arquivo:enviar", "arquivo:baixar",
              "painel:ler", "auditoria:ler", "usuario:gerenciar"},
    "GESTOR": {"doc:ler", "doc:criar", "doc:editar", "doc:arquivar", "arquivo:enviar", "arquivo:baixar",
               "painel:ler", "auditoria:ler"},
    "OPERADOR": {"doc:ler", "doc:criar", "doc:editar", "arquivo:enviar", "arquivo:baixar"},
    "CONSULTA": {"doc:ler", "arquivo:baixar"},
}

# Classificações que cada perfil pode ver (LAI: restrição legítima de acesso)
VISIBILIDADE: dict[str, tuple[str, ...]] = {
    "ADMIN": ("PUBLICO", "RESTRITO", "SIGILOSO"),
    "GESTOR": ("PUBLICO", "RESTRITO", "SIGILOSO"),
    "OPERADOR": ("PUBLICO", "RESTRITO"),
    "CONSULTA": ("PUBLICO",),
}


def tem(perfil: str, permissao: str) -> bool:
    return permissao in PERMISSOES.get(perfil, set())
