"""Base modular: validadores e permissão por perfil (os módulos de negócio são gerados com fabrica.py crud gerar)."""
import pytest

from app.modulos import routers
from app.modulos.validadores import cnpj_valido, cpf_valido, validar_cpf_cnpj


def test_descoberta_de_modulos_funciona():
    assert isinstance(routers(), list)


def test_validadores_cpf_cnpj():
    assert cpf_valido("52998224725") and not cpf_valido("11111111111")
    assert cnpj_valido("11222333000181") and not cnpj_valido("11222333000182")
    with pytest.raises(ValueError):
        validar_cpf_cnpj("123")
