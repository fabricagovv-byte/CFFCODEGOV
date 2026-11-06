# Requisitos — MOD-002 MOD-002 Correções de validação e privacidade (M03, M05, M07, M08)

| ID | Requisito | Origem | Implementado em | Teste que comprova | Situação |
|---|---|---|---|---|---|
| R1 | Publicação visível apenas no estado permitido | TR M03 critério de aceite; achado 3 | app/main.py `posts`, `overview` | test_leitor_ve_somente_publicadas, test_painel_do_leitor_conta_somente_publicadas | EXECUTADO e testado |
| R2 | Contato inexistente → 404 | Achado 4 | app/main.py `ticket_create` | test_chamado_com_contato_inexistente_responde_404 | EXECUTADO e testado |
| R3 | CSV sem fórmulas | RNF-06; achado 5 | app/main.py `celula_segura` | test_csv_neutraliza_formulas | EXECUTADO e testado |
| R4 | Canal da campanha existe | Achado 10 | app/main.py `campaign_create`; migração 0003 | test_campanha_com_canal_inexistente_responde_404, test_campanha_com_canal_valido, test_campanha_tem_chave_estrangeira_para_canal | EXECUTADO e testado |
| R5 | E-mail válido | TR M07; achado 11 | app/main.py `ContactIn` | test_email_invalido_e_recusado | EXECUTADO e testado |
| R6 | Leitor sem dados pessoais dos chamados | LGPD minimização; achado 12 | app/main.py `tickets` | test_leitor_nao_ve_descricao_nem_contato_dos_chamados | EXECUTADO e testado |
