"""MOD-100 — Base modular: descoberta automática de módulos, validadores e permissão por perfil."""
import pytest

from app.modulos import routers
from app.modulos.validadores import cnpj_valido, cpf_valido, validar_cpf_cnpj


def test_modulos_descobertos_e_registrados(client):
    prefixos = {r.prefix for r in routers()}
    assert {"/api/interessados", "/api/protocolos"} <= prefixos
    caminhos = client.get("/api/openapi.json").json()["paths"]
    assert "/api/interessados" in caminhos and "/api/protocolos/{rid}" in caminhos


def test_validadores_cpf_cnpj():
    assert cpf_valido("52998224725") and not cpf_valido("52998224724") and not cpf_valido("11111111111")
    assert cnpj_valido("11222333000181") and not cnpj_valido("11222333000182")
    assert validar_cpf_cnpj("529.982.247-25") == "52998224725"
    with pytest.raises(ValueError):
        validar_cpf_cnpj("123")


def test_exigir_perfil_bloqueia_quem_nao_pode(client, usuarios):
    # escrita em interessados é proibida ao perfil CONSULTA
    r = client.post("/api/interessados", json={"nome": "X", "documento": "52998224725", "tipo_pessoa": "FISICA"},
                    headers=usuarios["CONSULTA"])
    assert r.status_code == 403
    assert client.get("/api/interessados", headers=usuarios["CONSULTA"]).status_code == 200


def test_tabelas_dos_modulos_no_metadata():
    from app.db import Base
    assert {"interessados", "protocolos"} <= set(Base.metadata.tables)
