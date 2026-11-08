import pytest
from sqlalchemy import func, select

from app.bootstrap import ErroBootstrap, criar_primeiro_admin, politica_senha


def test_cria_o_primeiro_admin_e_recusa_o_segundo(cliente):
    from app.db import _fabrica_sessoes
    from app.modelos import Usuario
    uid = criar_primeiro_admin("dono", "Dono da Fábrica", "senha-forte-2026")
    assert uid > 0
    with _fabrica_sessoes()() as s:
        u = s.get(Usuario, uid)
        assert u.perfil == "ADMIN" and u.senha_hash != "senha-forte-2026"
    with pytest.raises(ErroBootstrap, match="já existem usuários"):
        criar_primeiro_admin("outro", "Outro", "senha-forte-2026")


def test_politica_de_senha_e_perfil(cliente):
    with pytest.raises(ErroBootstrap, match="12 caracteres"):
        politica_senha("curta1")
    with pytest.raises(ErroBootstrap, match="letras e números"):
        politica_senha("somente-letras-aqui")
    with pytest.raises(ErroBootstrap, match="ADMIN"):
        criar_primeiro_admin("x", "X", "senha-forte-2026", perfil="CONSULTA")
