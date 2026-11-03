# Equipe de agentes da Fábrica

Gerado por `fabrica.py agentes gerar` a partir de `fabrica/agentes/registry.yaml`.

## Fábrica Governamental (G01–G20)

| ID | Agente | Função | Ferramentas | Equivale |
|---|---|---|---|---|
| G01 | Diretor-Geral da Fábrica | Coordena a fábrica, prioridades, equipes, prazos, bloqueios e consolidação de entregas. | documentacao |  |
| G02 | Analista de Editais | Interpreta edital, TR, contrato e anexos e cria a matriz de rastreabilidade. | documentacao |  |
| G03 | Gestor Contratual | Controla vigência, OS, prazos, obrigações, entregáveis, riscos e aceites. | documentacao |  |
| G04 | Planejador GEC | Produz o Plano de Gestão da Execução Contratual e seus planos derivados. | documentacao |  |
| G05 | Arquiteto de Software | Define arquitetura, tecnologias compatíveis com o contrato, módulos, APIs e padrões. | documentacao |  |
| G06 | Programador Backend | Desenvolve APIs, serviços, autenticação, autorização, validação, logs e testes. | desenvolvimento |  |
| G07 | Programador Frontend | Desenvolve telas, formulários, dashboards, componentes, acessibilidade e preview. | desenvolvimento |  |
| G08 | Engenheiro de Banco de Dados | Modela dados, migrações, índices, integridade, permissões, backup e restauração. | desenvolvimento |  |
| G09 | Engenheiro de Integrações | Conecta sistemas por APIs, webhooks, filas e sincronização com tratamento de falhas. | desenvolvimento |  |
| G10 | Especialista em Segurança e LGPD | Protege sistemas e dados pessoais; analisa riscos, acessos, segredos e vulnerabilidades. | analise |  |
| G11 | DevOps e Infraestrutura | Dockerfiles, Compose, CI/CD, TLS, proxy, monitoramento, backup, rollback e DR. | desenvolvimento |  |
| G12 | Engenheiro de Testes | Cria e executa testes unitários, integração, API, interface, regressão e desempenho. | desenvolvimento |  |
| G13 | Revisor de Código | Revisão independente de arquitetura, código limpo, duplicações, erros e cobertura. | analise |  |
| G14 | Comunicador entre Agentes | Mantém o quadro, mensagens, decisões, handoffs, bloqueios e evita conflito de arquivos. | documentacao |  |
| G15 | Medidor de UST | Mede produção por UST conforme a tabela contratual, com memória de cálculo. | documentacao |  |
| G16 | Analista de Pontos de Função | Contagem de pontos de função pela metodologia contratada (IFPUG/NESMA/SISP). | documentacao |  |
| G17 | Auditor de Evidências | Confere arquivos, commits, testes, logs, capturas, medições e responsáveis. | analise |  |
| G18 | Gestor de Profissionais Reais | Cadastra a equipe humana e registra orientações, revisões, correções e aprovações reais. | documentacao |  |
| G19 | Gerador de Relatórios | Gera relatórios diário, semanal, mensal, por módulo, profissional, OS, medição e final. | documentacao |  |
| G20 | Homologador Técnico | Verifica critérios de aceite e prepara o checklist de homologação para aprovação humana. | analise |  |

## Engenharia de Software (E01–E20)

| ID | Agente | Função | Ferramentas | Equivale |
|---|---|---|---|---|
| E01 | Diretor de Engenharia de Software | Coordena o time de engenharia, prioridades, recursos e impedimentos técnicos. | documentacao | G01 |
| E02 | Líder Técnico (Tech Lead) | Transforma requisitos em tarefas técnicas com critérios objetivos e coordena a integração. | desenvolvimento |  |
| E03 | Arquiteto de Software (Engenharia) | Padrões, contratos de API, escalabilidade e decisões técnicas do time. | documentacao | G05 |
| E04 | Líder de Backend | Organiza serviços, APIs, autenticação, autorização e regras de negócio. | desenvolvimento |  |
| E05 | Desenvolvedor Backend I | APIs REST, validação de dados, serviços e testes unitários. | desenvolvimento |  |
| E06 | Desenvolvedor Backend II | Regras de negócio, processamento de dados, serviços internos e otimização. | desenvolvimento |  |
| E07 | Desenvolvedor Backend III | Integrações, processamento assíncrono, filas, webhooks e rotinas. | desenvolvimento |  |
| E08 | Líder de Frontend | Arquitetura de interfaces, componentes reutilizáveis, padrões visuais e acessibilidade. | desenvolvimento |  |
| E09 | Desenvolvedor Frontend I | Telas, navegação, componentes e formulários. | desenvolvimento |  |
| E10 | Desenvolvedor Frontend II | Dashboards, tabelas, filtros, relatórios visuais e telas administrativas. | desenvolvimento |  |
| E11 | Desenvolvedor Frontend III | Integração com APIs, estado, tratamento de erros e testes de interface. | desenvolvimento |  |
| E12 | Engenheiro de Banco de Dados (Engenharia) | Modelagem, migrações, índices, desempenho, backup e restauração. | desenvolvimento | G08 |
| E13 | Engenheiro de Integrações (Engenharia) | APIs externas, autenticação de serviços, sincronização e falhas. | desenvolvimento | G09 |
| E14 | Especialista em Segurança e LGPD (Engenharia) | Segurança de aplicação, segredos, auditoria e LGPD no dia a dia do time. | analise | G10 |
| E15 | Engenheiro DevOps (Engenharia) | Contêineres, CI/CD, ambientes, monitoramento e recuperação. | desenvolvimento | G11 |
| E16 | Coordenador de Qualidade (QA Lead) | Estratégia de testes, critérios de qualidade e controle de defeitos. | documentacao |  |
| E17 | Engenheiro de Automação de Testes | Testes unitários, integração, API, interface e regressão automatizados. | desenvolvimento | G12 |
| E18 | Revisor de Código (Engenharia) | Revisão independente e recomendações de refatoração. | analise | G13 |
| E19 | Documentador Técnico e Auditor de Evidências | Documentação de arquitetura, APIs, instalação e operação; verifica evidências. | documentacao | G17 |
| E20 | Coordenador de Comunicação e Sprints | Distribui tarefas do sprint, registra decisões e dependências e atualiza o quadro. | documentacao | G14 |

## Perfis de ferramentas (menor privilégio)

- **leitura**: Read, Grep, Glob
- **analise**: Read, Grep, Glob, Bash
- **documentacao**: Read, Grep, Glob, Bash, Write, Edit
- **desenvolvimento**: Read, Grep, Glob, Bash, Write, Edit
