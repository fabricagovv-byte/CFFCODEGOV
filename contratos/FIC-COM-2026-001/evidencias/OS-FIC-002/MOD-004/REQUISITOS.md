# Requisitos — MOD-004 MOD-004 Painel da fábrica — chave de acesso (ferramenta interna)

| ID | Requisito | Origem | Implementado em | Teste que comprova | Situação |
|---|---|---|---|---|---|
| R1 | API exige chave | Achado 2; minuta cl. 8 | FABRICA/app/main.py middleware | test_api_exige_a_chave_certa, test_api_sem_chave_configurada_fica_fechada, test_chave_curta_nao_abre_a_api | EXECUTADO e testado |
| R2 | Tela de acesso e cabeçalhos | Achado 2; RNF-06 | FABRICA/static/* | test_pagina_e_saude_abrem_sem_chave, test_cabecalhos_de_seguranca, test_pagina_sem_script_nem_estilo_embutido, test_painel_envia_a_chave_nas_chamadas | EXECUTADO e testado |
| R3 | Painel carrega sem erro | Achado 1 | FABRICA/static/painel.js | test_script_do_painel_compila, test_escape_html_cobre_apostrofo | EXECUTADO e testado |
| R4 | Fluxo original preservado | Pacote | FABRICA/app/core.py | test_workflow, test_human_hours | EXECUTADO e testado |
