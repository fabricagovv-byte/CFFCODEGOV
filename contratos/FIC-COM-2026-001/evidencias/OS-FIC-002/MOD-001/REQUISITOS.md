# Requisitos — MOD-001 MOD-001 Controle de sessão (TR M01, item 2 de 4)

| ID | Requisito | Origem | Implementado em | Teste que comprova | Situação |
|---|---|---|---|---|---|
| R1 | Sair encerra a sessão no servidor | TR M01 controle de sessão; achado 7 | app/main.py `logout`, `current` | test_sair_revoga_o_token_no_servidor, test_sair_encerra_somente_a_propria_sessao | EXECUTADO e testado |
| R2 | Token de sessão inexistente é recusado | TR M01 | app/security.py, app/main.py `current` | test_token_de_sessao_inexistente_e_recusado | EXECUTADO e testado |
| R3 | Limite de tentativas de login | TR RNF-01/RNF-06; achado 6 | app/main.py `login`, `_falhas` | test_bloqueio_apos_cinco_erros..., test_bloqueio_vale_por_usuario, test_tentativas_antigas_nao_bloqueiam | EXECUTADO e testado |
| R4 | Login e bloqueio auditados sem senha | TR M17; minuta cl. 8 | app/main.py `login` | test_login_ok_e_falho_ficam_na_auditoria, test_auditoria_de_falha_nao_guarda_senha, test_bloqueio_fica_registrado_na_auditoria | EXECUTADO e testado |
