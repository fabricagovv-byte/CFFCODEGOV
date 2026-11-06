def test_migracoes_vao_e_voltam_e_batem_com_os_modelos():
    from conftest import _alembic
    _alembic("downgrade", "base")
    _alembic("upgrade", "head")
    _alembic("check")
