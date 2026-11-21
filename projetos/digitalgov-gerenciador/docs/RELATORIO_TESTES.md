# Relatório de testes reais

Execução: 2026-11-06 20:21 (horário do servidor de testes). Banco: PostgreSQL 16 real, com bancos de teste separados. Arquivos de resultado (JUnit) em `docs/resultados_testes/`.

## Gerenciador central: 45 de 45 passaram

| Arquivo de teste | Testes | Resultado |
|---|---|---|
| `test_acesso` | 8 | passou |
| `test_backup` | 1 | passou |
| `test_cadastros` | 11 | passou |
| `test_cli` | 5 | passou |
| `test_documentos` | 3 | passou |
| `test_horas` | 6 | passou |
| `test_migracoes` | 1 | passou |
| `test_relatorios` | 4 | passou |
| `test_start_e_situacao` | 6 | passou |

<details><summary>Lista de testes</summary>

- `test_acesso` · test_login_e_dados_do_usuario — passou
- `test_acesso` · test_sem_login_nao_entra — passou
- `test_acesso` · test_senha_errada — passou
- `test_acesso` · test_bloqueio_apos_cinco_erros — passou
- `test_acesso` · test_sair_encerra_a_sessao — passou
- `test_acesso` · test_perfil_consulta_nao_altera — passou
- `test_acesso` · test_so_admin_exclui_e_cria_usuario — passou
- `test_acesso` · test_senha_guardada_com_scrypt_e_sem_aparecer — passou
- `test_backup` · test_backup_e_restauracao_do_banco_central — passou
- `test_cadastros` · test_cadastro_completo_e_filtro — passou
- `test_cadastros` · test_validacoes_do_contrato — passou
- `test_cadastros` · test_alteracao_parcial_respeita_as_regras — passou
- `test_cadastros` · test_os_autorizada_precisa_de_responsavel — passou
- `test_cadastros` · test_relacionamento_inexistente_responde_409 — passou
- `test_cadastros` · test_projeto_guarda_so_o_nome_da_variavel_do_banco — passou
- `test_cadastros` · test_profissional_so_com_cpf_mascarado — passou
- `test_cadastros` · test_agente_tarefa_evidencia — passou
- `test_cadastros` · test_medicao_aceita_precisa_de_documento — passou
- `test_cadastros` · test_resumo_da_medicao_do_contrato — passou
- `test_cadastros` · test_auditoria_registra_antes_e_depois — passou
- `test_cli` · test_importar_profissionais_ignora_exemplos_e_cpf_completo — passou
- `test_cli` · test_importar_agentes_da_fabrica — passou
- `test_cli` · test_criar_projeto_a_partir_do_modelo — passou
- `test_cli` · test_gravar_env_protege_o_arquivo — passou
- `test_cli` · test_criar_projeto_com_banco_isolado_no_postgresql — passou
- `test_documentos` · test_anexar_e_baixar_edital — passou
- `test_documentos` · test_recusa_formato_tamanho_e_tipo — passou
- `test_documentos` · test_arquivo_alterado_no_disco_e_recusado — passou
- `test_horas` · test_lancamento_calcula_horas_liquidas — passou
- `test_horas` · test_regras_do_lancamento — passou
- `test_horas` · test_totais_separam_humanas_aceitas_e_ia — passou
- `test_horas` · test_inconsistencias_sao_apontadas_sem_alterar_lancamentos — passou
- `test_horas` · test_aceite_so_para_horas_humanas_e_trava_correcao — passou
- `test_horas` · test_filtro_por_mes — passou
- `test_migracoes` · test_migracoes_vao_e_voltam_e_batem_com_os_modelos — passou
- `test_relatorios` · test_relatorio_de_horas_em_word_pdf_e_excel — passou
- `test_relatorios` · test_relatorio_de_medicao — passou
- `test_relatorios` · test_exportar_cadastros_para_excel — passou
- `test_relatorios` · test_painel — passou
- `test_start_e_situacao` · test_start_bloqueia_sem_contrato_e_sem_os_autorizada — passou
- `test_start_e_situacao` · test_start_bloqueia_sem_banco_configurado — passou
- `test_start_e_situacao` · test_start_completo_inicia_o_servico_e_mostra_integracao_pendente — passou
- `test_start_e_situacao` · test_situacao_nao_mostra_senha_do_banco — passou
- `test_start_e_situacao` · test_situacao_do_codigo_pelo_git — passou
- `test_start_e_situacao` · test_importar_resultado_dos_testes — passou

</details>

## Projeto de exemplo (proj-protocolo): 4 de 4 passaram

| Arquivo de teste | Testes | Resultado |
|---|---|---|
| `test_projeto` | 4 | passou |

<details><summary>Lista de testes</summary>

- `test_projeto` · test_saude_mostra_a_migracao — passou
- `test_projeto` · test_registro_e_gravado_no_banco — passou
- `test_projeto` · test_start_exige_o_token_do_gerenciador — passou
- `test_projeto` · test_migracoes_vao_e_voltam — passou

</details>

## Demonstração ponta a ponta (navegador)

Gerenciador (porta 8200) e projeto de exemplo (porta 8100) no ar, cada um com o próprio banco PostgreSQL; roteiro executado no Chromium (Playwright). Dados de demonstração identificados como DEMO.

| Passo | Resultado |
|---|---|
| Login do administrador | Entrou; painel com os cartões |
| START do projeto | Projeto ativo, contrato vigente, OS autorizada, banco `proj_protocolo` (migração 0001) e serviço OK; o projeto registrou o ciclo de produção nº 1; agentes: **Integração pendente** |
| Lançamento de horas pela tela | 8 h humanas registradas, 0 aceitas, 0 de IA; nenhuma inconsistência |
| Medição do contrato | 12.000 contratadas, 202,5 executadas, 0 aceitas, saldo 11.797,5, valor executado R$ 6.075,00 |
| Agentes | 44 importados da fábrica, todos com integração pendente |
| Projeto de exemplo | Registro gravado pela tela e listado a partir do banco do projeto |
| Erros de JavaScript | Nenhum |

Capturas em `docs/telas/`. Relatórios gerados pelo sistema em funcionamento em `docs/exemplos_relatorios/` (Word, PDF e Excel).

## Outras verificações

| Verificação | Resultado |
|---|---|
| Migrações do banco central: subir, descer e conferir com os modelos (`alembic check`) | Passou |
| Isolamento: usuário do projeto tentando entrar no banco do gerenciador | Recusado pelo PostgreSQL |
| Criação de projeto com banco próprio pela linha de comando | Banco, usuário e `.env` (permissão 600) criados; senha não exibida |
| Backup e restauração reais (pg_dump/pg_restore) com SHA-256 | Dados e documentos voltaram; arquivo alterado foi recusado |
| `iniciar.sh` (Linux) | Subiu o painel e respondeu `/api/health` |
| `docker compose config` (gerenciador e projeto) | Válido |

## O que não foi testado aqui

- **Construção das imagens Docker:** o serviço Docker não está disponível nesta máquina; a construção roda na CI do GitHub (etapa `gerenciador`).
- **`iniciar.ps1` (Windows):** escrito e revisado, mas não executado (esta máquina é Linux).
- **Integração com agentes (Codex):** não existe conector; o sistema mostra "Integração pendente" e não simula execução.

Total: 49 testes automatizados, todos passaram.
