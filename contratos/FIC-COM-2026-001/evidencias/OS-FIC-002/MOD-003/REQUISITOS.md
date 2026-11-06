# Requisitos — MOD-003 MOD-003 Base técnica — migrações versionadas, cabeçalhos de segurança, dependências

| ID | Requisito | Origem | Implementado em | Teste que comprova | Situação |
|---|---|---|---|---|---|
| R1 | Migrações em banco vazio com reversão | TR seção 6; achado 8 | app/migrations.py, migrations/ | test_migracoes_em_banco_vazio_e_reversao, test_upgrade_e_idempotente, migracoes-ida-e-volta | EXECUTADO e testado |
| R2 | Banco antigo reconhecido | Compatibilidade com o pacote | app/migrations.py `_conectar` | test_banco_antigo_do_pacote_e_reconhecido_sem_perder_dados | EXECUTADO e testado |
| R3 | Cabeçalhos de segurança | RNF-06; achado 9 | app/main.py middleware | test_cabecalhos_de_seguranca, test_api_nao_fica_em_cache, test_tela_nao_usa_estilo_inline_bloqueado_pela_csp | EXECUTADO e testado |
| R4 | Dependências fixas | Achado 13 | requirements.txt | test_dependencias_com_versao_fixa | EXECUTADO e testado |
