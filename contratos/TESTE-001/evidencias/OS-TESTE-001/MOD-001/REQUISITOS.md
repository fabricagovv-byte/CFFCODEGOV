# Requisitos — MOD-001 Autenticação e controle de acesso

| ID | Requisito | Origem | Implementado em | Teste que comprova | Situação |
|---|---|---|---|---|---|
| REQ-001 | Login | Prompt mestre | `app/routers/auth.py` | `test_login_sucesso_retorna_token_e_usuario` | IMPLEMENTADO — ver TESTES.json |
| REQ-002 | Logout | Prompt mestre | `app/routers/auth.py` | `test_logout_revoga_token` | IMPLEMENTADO — ver TESTES.json |
| REQ-003 | Recuperação de senha | Prompt mestre | `app/routers/auth.py` | `test_recuperacao_e_redefinicao_de_senha` | IMPLEMENTADO — ver TESTES.json |
| REQ-004 | Perfis e permissões | Prompt mestre | `app/permissions.py, app/deps.py` | `test_somente_admin_gerencia_usuarios` | IMPLEMENTADO — ver TESTES.json |
