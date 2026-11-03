# Requisitos — MOD-100 Base modular para cadastros

| ID | Requisito | Implementado em | Teste que comprova | Situação |
|---|---|---|---|---|
| BASE-1 | Novo módulo não exige editar main.py | app/modulos/__init__.py | test_modulos_descobertos_e_registrados | IMPLEMENTADO |
| BASE-2 | Validar CPF/CNPJ | app/modulos/validadores.py | test_validadores_cpf_cnpj | IMPLEMENTADO |
| BASE-3 | Permissão por perfil por módulo | app/deps.py exigir_perfil | test_exigir_perfil_bloqueia_quem_nao_pode | IMPLEMENTADO |
