# Arquitetura — MOD-100 Base modular para cadastros

`app/modulos/` com descoberta via pkgutil; `migrations/env.py` carrega modelos dos módulos para o Alembic; `tests/conftest.py` limpa todas as tabelas do metadata.
