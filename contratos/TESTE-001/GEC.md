# Plano de Gestão da Execução Contratual (GEC) — TESTE-001 (FICTÍCIO)

> Demonstração da fábrica. UST fictícias sem valor. Aprovação humana: **pendente**.

## 1. Identificação contratual
- Órgão: Órgão Fictício de Demonstração · Contrato: TESTE-001 · OS: OS-TESTE-001 · Regime: Lei 14.133/2021 (simulação)
- Vigência: 2026-11-03 a 2026-12-31 · Gestor/fiscal: a cadastrar

## 2. Escopo e objetivos
- **O quê:** sistema web de Gestão Documental Pública (cadastro, PDF, pesquisa, painel, auditoria).
- **Por quê:** validar de ponta a ponta a fábrica (agentes, evidências, medição, relatórios, entrega) antes de contratos reais.
- **Como:** FastAPI + React + PostgreSQL em Docker; 7 módulos; testes por módulo; evidências por módulo.
- **Fora do escopo:** integração gov.br, SMTP real, antivírus, publicação em servidor.

## 3. Requisitos
Ver `MATRIZ_RASTREABILIDADE.md` (REQ-001 a REQ-013).

## 4. Módulos
| ID | Nome | Responsável humano | Agentes | Prazo | Depende de | Medição | Testes | Aceite |
|---|---|---|---|---|---|---|---|---|
| MOD-007 | Infraestrutura e documentação | A CADASTRAR | G05, G11, G08, E15, G19 | 2026-11-03 | — | 1 UST | pytest infra, build, alembic check, Docker e2e | ambiente sobe e restaura backup |
| MOD-001 | Autenticação e controle de acesso | A CADASTRAR | G06, E05, G07, E09, G10, G12 | 2026-11-03 | MOD-007 | 2 UST | 17 backend + 3 frontend | testes ok + revisão humana |
| MOD-002 | Cadastro documental | A CADASTRAR | G06, E06, G07, E09, G12 | 2026-11-03 | MOD-001 | 2 UST | backend + frontend | idem |
| MOD-003 | Upload de PDF | A CADASTRAR | G06, E07, G07, G10, G12 | 2026-11-03 | MOD-002 | 2 UST | backend + frontend | idem |
| MOD-004 | Pesquisa | A CADASTRAR | G06, E06, G07, E10 | 2026-11-03 | MOD-002 | 1 UST | backend + frontend | idem |
| MOD-005 | Painel administrativo | A CADASTRAR | G06, G07, E10 | 2026-11-03 | MOD-002 | 1 UST | backend + frontend | idem |
| MOD-006 | Auditoria | A CADASTRAR | G06, G08, G10, E11 | 2026-11-03 | MOD-001 | 1 UST | backend (+trigger PG) + frontend | idem |

## 5. Arquitetura e tecnologias
Ver `projetos/gestao-documental/docs/ARQUITETURA.md`.

## 6. Equipe humana e agentes
Nenhum profissional cadastrado (`PROFISSIONAIS.csv` vazio). Todo o trabalho desta OS foi executado por agentes de IA numa sessão do Claude Code e **aguarda revisão e aprovação humana**.

## 7. RACI
| Atividade | R | A | C | I |
|---|---|---|---|---|
| Planejamento | G04 | humano (gerente) | G02, G05 | G01 |
| Desenvolvimento | G06/G07 (E04–E11) | humano (responsável técnico) | G05 | G14 |
| Testes | G12/E17 | E16 | devs | G17 |
| Segurança | G10 | humano | G13 | G01 |
| Medição | G15 | humano + fiscal do órgão | G17 | G03 |
| Homologação | G20 | fiscal do órgão | G17 | G01 |

## 8. Cronograma e marcos
| Marco | Data | Entregáveis | Situação |
|---|---|---|---|
| M1 Fábrica configurada | 2026-11-03 | agentes, CLI, skills | executado |
| M2 Código + testes dos 7 módulos | 2026-11-03 | projetos/gestao-documental | executado e verificado |
| M3 Evidências + medição + checklist | 2026-11-03 | contratos/TESTE-001 | executado |
| M4 Revisão/aprovação humana | a definir | PARTICIPACOES.csv, REVISOES.md | pendente |
| M5 Homologação/aceite | a definir | ACEITE.md | pendente |

## 9. Metas diárias
Demonstração em um dia: 7 módulos. Em contratos reais, metas saem da capacidade histórica (`producao estatisticas`).

## 10. Riscos
| ID | Risco | Prob. | Impacto | Resposta | Dono |
|---|---|---|---|---|---|
| R1 | Ausência de responsável humano impede medição aceita | alta | alto | cadastrar profissionais | G18 |
| R2 | SMTP indisponível impede recuperação de senha em produção | média | médio | integrar SMTP do órgão | G11 |
| R3 | Limitador de login em memória com várias réplicas | média | médio | Redis | G10 |
| R4 | Limite de requisições do Docker Hub no build | média | baixo | espelho de registro / cache | G11 |

## 11. Comunicação
Quadro e mensagens em `fabrica/comunicacao/`; relatório diário em `relatorios/diarios/`.

## 12. Segurança e LGPD
`projetos/gestao-documental/docs/SEGURANCA_LGPD.md` + `SEGURANCA.md` de cada módulo.

## 13. Medição
Tabela `TABELA_UST.csv` (fictícia). Comprovado só com auditoria técnica aprovada; aceito só com termo do órgão.

## 14. Testes
pytest (SQLite e PostgreSQL), Vitest, typecheck/build, `alembic check`, e2e Docker com backup/restauração, capturas Playwright.

## 15–16. Homologação, implantação e continuidade
`docs/MANUAL_PUBLICACAO.md`, `docs/MANUAL_OPERACAO.md`, `docs/PLANO_CONTINUIDADE.md`.

## 17. Controle de mudanças
Mudança = nova tarefa no quadro + decisão registrada + aprovação humana.

## 18. Critérios de conclusão
15 evidências por módulo, auditoria APROVADO, checklist sem crítico reprovado, revisão humana registrada, aceite do órgão.
