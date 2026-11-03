# Checklist de 100 controles — OS-TESTE-002

Gerado em 2026-11-03T01:09:11-03:00.

**Situação da entrega: PENDENTE_VERIFICACAO_HUMANA**

Aprovados 41 · Reprovados 0 · Não aplicáveis 0 · Não verificados 59

Críticos aguardando verificação humana: C003, C009, C012, C024, C032, C037, C039, C041, C042, C043, C045, C047, C062, C087, C090, C099


## Contrato e requisitos

| ID | Controle | Crítico | Resultado | Evidência | Responsável |
|---|---|---|---|---|---|
| C001 | Documentos contratuais recebidos e registrados | sim | APROVADO | contratos/TESTE-002/contrato.yaml | G17 (automático) |
| C002 | Matriz de rastreabilidade com cláusula de origem | sim | APROVADO | contratos/TESTE-002/MATRIZ_RASTREABILIDADE.md | G17 (automático) |
| C003 | Ordem de serviço autorizada por responsável do contratante | sim | NAO_VERIFICADO | requer verificação humana |  |
| C004 | Escopo de cada módulo descrito | sim | APROVADO | ESCOPO.md em 3/3 módulos | G17 (automático) |
| C005 | Requisitos de cada módulo rastreados | sim | APROVADO | REQUISITOS.md em 3/3 módulos | G17 (automático) |
| C006 | Critérios de aceite definidos por módulo |  | APROVADO | contratos/TESTE-002/GEC.md | G17 (automático) |
| C007 | Conflitos entre documentos registrados e encaminhados |  | NAO_VERIFICADO | requer verificação humana |  |
| C008 | SLAs identificados e monitoráveis |  | NAO_VERIFICADO | requer verificação humana |  |
| C009 | Exigências de equipe confrontadas com profissionais cadastrados | sim | NAO_VERIFICADO | requer verificação humana |  |
| C010 | Legislação aplicável identificada para o ente contratante |  | NAO_VERIFICADO | requer verificação humana |  |

## Arquitetura

| ID | Controle | Crítico | Resultado | Evidência | Responsável |
|---|---|---|---|---|---|
| C011 | Arquitetura documentada | sim | APROVADO | ARQUITETURA.md em 3/3 módulos | G17 (automático) |
| C012 | Tecnologias compatíveis com o contrato | sim | NAO_VERIFICADO | requer verificação humana |  |
| C013 | Contratos de API documentados (OpenAPI) |  | APROVADO | projetos/gestao-documental/backend/app/main.py | G17 (automático) |
| C014 | Separação de camadas (rotas/serviços/modelos) |  | NAO_VERIFICADO | requer verificação humana |  |
| C015 | Requisitos não funcionais endereçados |  | NAO_VERIFICADO | requer verificação humana |  |
| C016 | Decisões técnicas registradas |  | NAO_VERIFICADO | requer verificação humana |  |
| C017 | Escalabilidade compatível com a demanda |  | NAO_VERIFICADO | requer verificação humana |  |
| C018 | Configuração externa por variáveis de ambiente |  | APROVADO | projetos/gestao-documental/.env.example | G17 (automático) |
| C019 | Dependências declaradas e versionadas |  | APROVADO | projetos/gestao-documental/backend/requirements.txt | G17 (automático) |
| C020 | Interoperabilidade (Lei 14.129/2021) avaliada quando aplicável |  | NAO_VERIFICADO | requer verificação humana |  |

## Código-fonte

| ID | Controle | Crítico | Resultado | Evidência | Responsável |
|---|---|---|---|---|---|
| C021 | Código existe no repositório | sim | APROVADO | projetos/gestao-documental/backend/app | G17 (automático) |
| C022 | Commits reais vinculados a cada módulo | sim | APROVADO | todos os módulos com commits reais | G17 (automático) |
| C023 | Tratamento de erros consistente |  | NAO_VERIFICADO | requer verificação humana |  |
| C024 | Validação de entradas em todas as APIs | sim | NAO_VERIFICADO | caso 'test_validacao_de_campos' não executado | G17 (automático) |
| C025 | Sem duplicação relevante |  | NAO_VERIFICADO | requer verificação humana |  |
| C026 | Tipagem aplicada (Python hints / TypeScript) |  | APROVADO | projetos/gestao-documental/frontend/tsconfig.json | G17 (automático) |
| C027 | Logs estruturados sem dados sensíveis |  | NAO_VERIFICADO | requer verificação humana |  |
| C028 | Revisão independente registrada | sim | APROVADO | REVISOES.md em 3/3 módulos | G17 (automático) |
| C029 | Padrão de código (lint) aplicado |  | NAO_VERIFICADO | requer verificação humana |  |
| C030 | Código-fonte entregável sem dependência de serviço proprietário não previsto |  | NAO_VERIFICADO | requer verificação humana |  |

## Banco de dados

| ID | Controle | Crítico | Resultado | Evidência | Responsável |
|---|---|---|---|---|---|
| C031 | Migrações versionadas | sim | APROVADO | projetos/gestao-documental/backend/migrations/versions | G17 (automático) |
| C032 | Migração aplicada em banco real | sim | NAO_VERIFICADO | caso 'verificar_ambiente' não executado | G17 (automático) |
| C033 | Integridade referencial (FKs) definida |  | NAO_VERIFICADO | requer verificação humana |  |
| C034 | Índices para consultas frequentes |  | NAO_VERIFICADO | requer verificação humana |  |
| C035 | Usuário de aplicação com menor privilégio |  | NAO_VERIFICADO | requer verificação humana |  |
| C036 | Rotina de backup documentada | sim | APROVADO | projetos/gestao-documental/infra/scripts/backup.sh | G17 (automático) |
| C037 | Restauração testada | sim | NAO_VERIFICADO | caso 'verificar_ambiente' não executado | G17 (automático) |
| C038 | Dicionário de dados |  | NAO_VERIFICADO | requer verificação humana |  |
| C039 | Dados de demonstração fictícios | sim | NAO_VERIFICADO | requer verificação humana |  |
| C040 | Retenção e expurgo definidos |  | NAO_VERIFICADO | requer verificação humana |  |

## Segurança e LGPD

| ID | Controle | Crítico | Resultado | Evidência | Responsável |
|---|---|---|---|---|---|
| C041 | Autenticação implementada e testada | sim | NAO_VERIFICADO | caso 'test_login_sucesso' não executado | G17 (automático) |
| C042 | Autorização por perfil (menor privilégio) | sim | NAO_VERIFICADO | caso 'test_visibilidade_por_classificacao' não executado | G17 (automático) |
| C043 | Senhas com hash forte (bcrypt/argon2) | sim | NAO_VERIFICADO | requer verificação humana |  |
| C044 | Nenhum segredo versionado | sim | APROVADO | nenhum padrão encontrado | G17 (automático) |
| C045 | Trilha de auditoria de ações sensíveis | sim | NAO_VERIFICADO | caso 'test_acoes_sensiveis_sao_auditadas' não executado | G17 (automático) |
| C046 | Inventário de dados pessoais e finalidade | sim | APROVADO | SEGURANCA.md em 3/3 módulos | G17 (automático) |
| C047 | TLS em homologação/produção | sim | NAO_VERIFICADO | requer verificação humana |  |
| C048 | Cabeçalhos de segurança HTTP |  | NAO_VERIFICADO | caso 'test_cabecalhos_de_seguranca' não executado | G17 (automático) |
| C049 | Proteção contra força bruta no login |  | NAO_VERIFICADO | caso 'test_bloqueio_por_forca_bruta' não executado | G17 (automático) |
| C050 | Plano de resposta a incidentes |  | NAO_VERIFICADO | requer verificação humana |  |

## Testes

| ID | Controle | Crítico | Resultado | Evidência | Responsável |
|---|---|---|---|---|---|
| C051 | Testes automatizados de backend executados sem falhas | sim | APROVADO | 33 testes, 0 falhas (contratos/TESTE-002/evidencias/OS-TESTE-002/MOD-102/LOGS_TESTES/backend-20261103T010440.xml) | G17 (automático) |
| C052 | Testes de frontend executados sem falhas | sim | APROVADO | 6 testes, 0 falhas (contratos/TESTE-002/evidencias/OS-TESTE-002/MOD-102/LOGS_TESTES/frontend-20261103T010445.xml) | G17 (automático) |
| C053 | Resultados registrados por módulo | sim | APROVADO | TESTES.json em 3/3 módulos | G17 (automático) |
| C054 | Logs de execução de testes anexados | sim | APROVADO | LOGS_TESTES em 3/3 módulos | G17 (automático) |
| C055 | Testes de API cobrem casos de erro |  | NAO_VERIFICADO | requer verificação humana |  |
| C056 | Testes de regressão no CI |  | APROVADO | .github/workflows/ci.yml | G17 (automático) |
| C057 | Testes contra banco igual ao de produção (PostgreSQL) |  | NAO_VERIFICADO | caso 'test_trigger_impede' não executado | G17 (automático) |
| C058 | Defeitos registrados e reexecutados |  | NAO_VERIFICADO | requer verificação humana |  |
| C059 | Testes de interface (E2E/captura) |  | NAO_VERIFICADO | requer verificação humana |  |
| C060 | Ferramenta da fábrica testada |  | NAO_VERIFICADO | nenhuma execução encontrada | G17 (automático) |

## Desempenho

| ID | Controle | Crítico | Resultado | Evidência | Responsável |
|---|---|---|---|---|---|
| C061 | Paginação em listagens |  | NAO_VERIFICADO | requer verificação humana |  |
| C062 | Limite de tamanho de upload | sim | NAO_VERIFICADO | caso 'test_rejeita_arquivo_acima_do_limite' não executado | G17 (automático) |
| C063 | Consultas indexadas |  | NAO_VERIFICADO | requer verificação humana |  |
| C064 | Tempo de resposta medido |  | NAO_VERIFICADO | requer verificação humana |  |
| C065 | Build de frontend otimizado |  | NAO_VERIFICADO | caso 'npm run build' não executado | G17 (automático) |
| C066 | Compressão e cache de estáticos |  | NAO_VERIFICADO | requer verificação humana |  |
| C067 | Pool de conexões configurado |  | NAO_VERIFICADO | requer verificação humana |  |
| C068 | Arquivos armazenados fora do banco |  | NAO_VERIFICADO | requer verificação humana |  |
| C069 | Capacidade estimada documentada |  | NAO_VERIFICADO | requer verificação humana |  |
| C070 | Teste de carga executado quando exigido |  | NAO_VERIFICADO | requer verificação humana |  |

## Infraestrutura

| ID | Controle | Crítico | Resultado | Evidência | Responsável |
|---|---|---|---|---|---|
| C071 | Dockerfiles presentes | sim | APROVADO | projetos/gestao-documental/backend/Dockerfile | G17 (automático) |
| C072 | Docker Compose do ambiente | sim | APROVADO | projetos/gestao-documental/docker-compose.yml | G17 (automático) |
| C073 | Pipeline CI/CD |  | APROVADO | .github/workflows/ci.yml | G17 (automático) |
| C074 | Ambientes dev/homologação/produção separados |  | NAO_VERIFICADO | requer verificação humana |  |
| C075 | Proxy reverso com TLS documentado | sim | APROVADO | projetos/gestao-documental/infra/nginx | G17 (automático) |
| C076 | Healthchecks configurados |  | NAO_VERIFICADO | caso 'test_health_e_banco' não executado | G17 (automático) |
| C077 | Monitoramento e logs centralizáveis |  | NAO_VERIFICADO | requer verificação humana |  |
| C078 | Procedimento de rollback | sim | APROVADO | projetos/gestao-documental/docs/MANUAL_PUBLICACAO.md | G17 (automático) |
| C079 | Plano de recuperação de desastres |  | APROVADO | projetos/gestao-documental/docs/PLANO_CONTINUIDADE.md | G17 (automático) |
| C080 | Imagens construídas e ambiente subido via Compose |  | NAO_VERIFICADO | caso 'verificar_ambiente' não executado | G17 (automático) |

## Evidências e medição

| ID | Controle | Crítico | Resultado | Evidência | Responsável |
|---|---|---|---|---|---|
| C081 | Pasta de evidências por módulo | sim | APROVADO | ESCOPO.md em 3/3 módulos | G17 (automático) |
| C082 | CODIGO_ALTERADO.md por módulo | sim | APROVADO | CODIGO_ALTERADO.md em 3/3 módulos | G17 (automático) |
| C083 | COMMITS.json por módulo | sim | APROVADO | COMMITS.json em 3/3 módulos | G17 (automático) |
| C084 | Responsáveis humanos registrados | sim | APROVADO | RESPONSAVEIS.md em 3/3 módulos | G17 (automático) |
| C085 | Memória de cálculo da medição | sim | APROVADO | contratos/TESTE-002/medicoes/OS-TESTE-002.json | G17 (automático) |
| C086 | Separação previsto / comprovado / aceito | sim | APROVADO | contratos/TESTE-002/medicoes/OS-TESTE-002.json | G17 (automático) |
| C087 | Nenhuma equivalência UST/PF/horas inventada | sim | NAO_VERIFICADO | requer verificação humana |  |
| C088 | Capturas reais quando há interface |  | NAO_VERIFICADO | requer verificação humana |  |
| C089 | Auditoria de evidências executada | sim | APROVADO | evidencias/OS-TESTE-002/AUDITORIA.md (2026-11-03T01:05) | G17 (automático) |
| C090 | Participação humana com origem registrada | sim | NAO_VERIFICADO | requer verificação humana |  |

## Documentação e homologação

| ID | Controle | Crítico | Resultado | Evidência | Responsável |
|---|---|---|---|---|---|
| C091 | README de execução local | sim | APROVADO | projetos/gestao-documental/README.md | G17 (automático) |
| C092 | Manual de publicação | sim | APROVADO | projetos/gestao-documental/docs/MANUAL_PUBLICACAO.md | G17 (automático) |
| C093 | Manual de operação e manutenção |  | APROVADO | projetos/gestao-documental/docs/MANUAL_OPERACAO.md | G17 (automático) |
| C094 | Documentação de API |  | NAO_VERIFICADO | caso 'test_openapi_publicado' não executado | G17 (automático) |
| C095 | PREVIEW.md por módulo |  | APROVADO | PREVIEW.md em 3/3 módulos | G17 (automático) |
| C096 | IMPLANTACAO.md por módulo |  | APROVADO | IMPLANTACAO.md em 3/3 módulos | G17 (automático) |
| C097 | ACEITE.md com situação real | sim | APROVADO | ACEITE.md em 3/3 módulos | G17 (automático) |
| C098 | Checklist de homologação preparado |  | NAO_VERIFICADO | requer verificação humana |  |
| C099 | Aprovação humana técnica registrada | sim | NAO_VERIFICADO | requer verificação humana |  |
| C100 | Aceite formal do contratante (não confundir com aprovação técnica) |  | NAO_VERIFICADO | requer verificação humana |  |

Para registrar verificação humana: edite `checklist/resultados_humanos.yaml` (resultado, responsavel, evidencia, data) e rode o checklist de novo.
