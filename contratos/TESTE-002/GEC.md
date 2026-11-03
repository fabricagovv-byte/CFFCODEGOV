# Plano de Gestão da Execução Contratual (GEC) — TESTE-002

Gerado em 2026-11-03T06:49:19-03:00 pelo Planejador GEC (G04) com apoio de G02, G21, G22, G23 e G24. Itens **a preencher** dependem do edital ou do responsável.

> **Legenda:** ESTIMATIVA = planejado/calculado antes da execução · REAL = comprovado (auditado) ou aceito pelo órgão. Cada exigência indica a origem (documento, cláusula, página).

## 1. Identificação do contrato

| Campo | Valor |
|---|---|
| Órgão contratante | Órgão Fictício de Demonstração |
| Esfera | municipal |
| Contrato / processo / edital | TESTE-002 / **a preencher** / **a preencher** |
| Regime jurídico | Lei 14.133/2021 (simulação) |
| Vigência | 2026-11-03 a 2027-03-31 |
| Valor global | **a preencher** |
| Gestor / fiscal do contrato | **a preencher** / **a preencher** |
| Preposto da contratada | **a preencher** |

## 2. Objeto e escopo

**Objeto:** Atendimento ao cidadão e protocolo (demonstração da fábrica — FICTÍCIO)

Tecnologias obrigatórias: React, FastAPI, PostgreSQL · Banco: PostgreSQL 16 · Infraestrutura: **a preencher**

Matriz de rastreabilidade completa: `MATRIZ_RASTREABILIDADE.md`.

## 3. Serviços contratados — explicação técnica

| Código | Serviço | Explicação técnica | Unidade | Origem |
|---|---|---|---|---|
| SRV-BASE | Estrutura base de módulos | Infraestrutura que permite adicionar cadastros como módulos independentes: descoberta automática de modelos e rotas, validadores e permissões por perfil. | UST | FICTÍCIO — catálogo demo item 1 |
| SRV-CRUD-M | Cadastro média complexidade | Cadastro completo de uma entidade sem relacionamentos complexos: tabela e migração, API REST com validação, busca e paginação, exclusão lógica, auditoria, tela com lista e formulário, testes de API e de tela. | UST | FICTÍCIO — catálogo demo item 2 |
| SRV-CRUD-A | Cadastro alta complexidade com relacionamentos | Como o de média complexidade, com relacionamentos entre tabelas (chave estrangeira validada), listas de opções, campos monetários e de data e mais regras de validação. | UST | FICTÍCIO — catálogo demo item 3 |
| SRV-REL | Relatório gerencial com filtros | Consulta agregada com filtros por período e categoria, tabela e exportação, com testes dos totais. | UST | FICTÍCIO — catálogo demo item 4 |

**Catálogo de serviços × perfis (horas por execução):**

| Serviço | Perfil | Horas | Origem |
|---|---|---|---|
| SRV-BASE — Estrutura base de módulos (FICTÍCIO) | DESENVOLVEDOR_SENIOR | 8 | Catálogo fictício item 1 |
| SRV-BASE — Estrutura base de módulos (FICTÍCIO) | ANALISTA_TESTES | 2 | Catálogo fictício item 1 |
| SRV-CRUD-M — Cadastro completo média complexidade (FICTÍCIO) | ANALISTA_REQUISITOS | 4 | Catálogo fictício item 2 |
| SRV-CRUD-M — Cadastro completo média complexidade (FICTÍCIO) | DESENVOLVEDOR_PLENO | 16 | Catálogo fictício item 2 |
| SRV-CRUD-M — Cadastro completo média complexidade (FICTÍCIO) | ANALISTA_TESTES | 4 | Catálogo fictício item 2 |
| SRV-CRUD-A — Cadastro completo alta complexidade com relacionamentos (FICTÍCIO) | ANALISTA_REQUISITOS | 6 | Catálogo fictício item 3 |
| SRV-CRUD-A — Cadastro completo alta complexidade com relacionamentos (FICTÍCIO) | DESENVOLVEDOR_SENIOR | 24 | Catálogo fictício item 3 |
| SRV-CRUD-A — Cadastro completo alta complexidade com relacionamentos (FICTÍCIO) | ANALISTA_TESTES | 6 | Catálogo fictício item 3 |
| SRV-REL — Relatório gerencial com filtros (FICTÍCIO) | DESENVOLVEDOR_PLENO | 12 | Catálogo fictício item 4 |
| SRV-REL — Relatório gerencial com filtros (FICTÍCIO) | ANALISTA_TESTES | 3 | Catálogo fictício item 4 |

## 4. Equipe exigida × equipe designada

| Perfil exigido | Qtd | Requisitos | Origem |
|---|---|---|---|
| Desenvolvedor Sênior | 1 | 5 anos | FICTÍCIO — TR demo 7.1 |
| Analista de Testes | 1 | — | FICTÍCIO — TR demo 7.2 |

**Designados:**

- Nomes a informar no final (a fábrica trabalha com os perfis; os nomes entram no cadastro da equipe antes da entrega).

Confronto completo edital × documento base: `CONFRONTO_EDITAL.md`.

## 5. Organização: agentes de IA e responsabilidade humana

| Etapa | Agentes de IA | Responsável humano (aprova) |
|---|---|---|
| Leitura do edital, habilitação, SLAs | G02, G21, G23 | Gestor do contrato |
| Planejamento, cronograma, custos | G04, G24, G22 | Gerente de projeto |
| Arquitetura e desenvolvimento | G05, G06–G09, E01–E13 | Responsável técnico |
| Testes, revisão, segurança | G12, G13, G10, E16–E18 | Responsável técnico |
| Evidências, medição, relatórios | G17, G15, G16, G19 | Gerente de projeto / preposto |
| Homologação e entrega | G20, G11 | Fiscal do órgão (aceite) |

Total: 44 agentes de IA (lista em `fabrica/docs/EQUIPE_AGENTES.md`).

## 6. Planejamento por projeto (ESTIMATIVA)

| Projeto | Módulos | UST | Horas | Valor | Início | Fim |
|---|---|---|---|---|---|---|
| ATENDIMENTO | 3 | 80,4 | 70 | R$ 7.800,00 | 2026-11-03 | 2026-11-06 |
| RELATORIOS | 2 | 29,4 | 30 | R$ 2.790,00 | 2026-11-09 | 2026-11-12 |

| Projeto | Módulo | Serviço | UST | Horas | Início | Fim | Responsável |
|---|---|---|---|---|---|---|---|
| ATENDIMENTO | MOD-100 Base modular para cadastros | SRV-BASE | 12,2 | 10 | 2026-11-03 | 2026-11-03 | a definir |
| ATENDIMENTO | MOD-101 Cadastro de interessados | SRV-CRUD-M | 24,4 | 24 | 2026-11-03 | 2026-11-04 | a definir |
| ATENDIMENTO | MOD-102 Cadastro de protocolos | SRV-CRUD-A | 43,8 | 36 | 2026-11-03 | 2026-11-06 | a definir |
| RELATORIOS | MOD-201 Relatório de protocolos por período | SRV-REL | 14,7 | 15 | 2026-11-09 | 2026-11-11 | a definir |
| RELATORIOS | MOD-202 Relatório de atendimento por canal | SRV-REL | 14,7 | 15 | 2026-11-10 | 2026-11-12 | a definir |

## 7. Cronograma diário (ESTIMATIVA)

| Dia | Módulos em execução | Meta (UST) | Horas | Valor |
|---|---|---|---|---|
| 2026-11-03 | MOD-100, MOD-101, MOD-102 | 35.35 | 31.0 | R$ 3.432,50 |
| 2026-11-04 | MOD-101, MOD-102 | 23.15 | 21.0 | R$ 2.222,50 |
| 2026-11-05 | MOD-102 | 10.95 | 9.0 | R$ 1.072,50 |
| 2026-11-06 | MOD-102 | 10.95 | 9.0 | R$ 1.072,50 |
| 2026-11-09 | MOD-201 | 4.90 | 5.0 | R$ 465,00 |
| 2026-11-10 | MOD-201, MOD-202 | 9.80 | 10.0 | R$ 930,00 |
| 2026-11-11 | MOD-201, MOD-202 | 9.80 | 10.0 | R$ 930,00 |
| 2026-11-12 | MOD-202 | 4.90 | 5.0 | R$ 465,00 |

## 8. Cronograma mensal e mensalidades (ESTIMATIVA)

| Mês | Dias úteis com execução | UST | Horas | Mensalidade estimada |
|---|---|---|---|---|
| 2026-11 | 8 | 109.80 | 100.0 | R$ 10.590,00 |

Pagamento conforme o contrato: mensal, após aceite definitivo da OS (FICTÍCIO — Contrato demo cláusula 6).

## 9. Medição e cálculos

- Modalidade: UST · Metodologia: Catálogo de serviços × perfis × horas (FICTÍCIO) · Fórmula: HORAS_X_FATOR
- Quantidade contratada: 300 UST · Valor unitário: **a preencher**
- Medição parcial: **a preencher**

| Perfil | Valor/hora | Fator UST/hora | Origem |
|---|---|---|---|
| ANALISTA_REQUISITOS | R$ 110,00 | 1.2 | Tabela fictícia de demonstração |
| DESENVOLVEDOR_SENIOR | R$ 130,00 | 1.3 | Tabela fictícia de demonstração |
| DESENVOLVEDOR_PLENO | R$ 95,00 | 1.0 | Tabela fictícia de demonstração |
| ANALISTA_TESTES | R$ 85,00 | 0.9 | Tabela fictícia de demonstração |

- Pontos de função: contagem pela metodologia do contrato (G16); produtividade h/PF não informada.
- Regras: previsto = OS; comprovado = auditoria aprovada; aceito = documento do órgão. UST/PF/horas só se convertem pela fórmula do contrato.

## 10. Custos estimados por perfil (ESTIMATIVA)

| Perfil | Horas planejadas | Valor/hora | Custo estimado |
|---|---|---|---|
| ANALISTA_REQUISITOS | 10 | R$ 110,00 | R$ 1.100,00 |
| ANALISTA_TESTES | 18 | R$ 85,00 | R$ 1.530,00 |
| DESENVOLVEDOR_PLENO | 40 | R$ 95,00 | R$ 3.800,00 |
| DESENVOLVEDOR_SENIOR | 32 | R$ 130,00 | R$ 4.160,00 |
| **Total** | **100** | | **R$ 10.590,00** |

## 11. Documentos de habilitação

| Grupo | Documento | Exigência | Origem | Situação |
|---|---|---|---|---|
| Habilitação jurídica | Ato constitutivo e alterações | vigente | FICTÍCIO — Edital demo 9.1 | a verificar |
| Regularidade fiscal e trabalhista | CND federal, FGTS, CNDT | válidas na data da sessão | FICTÍCIO — Edital demo 9.2 | a verificar |
| Qualificação técnica | Atestado de capacidade técnica | desenvolvimento de sistema web com banco relacional | FICTÍCIO — Edital demo 9.3 | a verificar |
| Econômico-financeira | Balanço patrimonial e certidão de falência | último exercício | FICTÍCIO — Edital demo 9.4 | a verificar |

## 12. Níveis de serviço (SLA) e glosas

| Indicador | Meta | Como medir | Glosa | Origem |
|---|---|---|---|---|
| Prazo de entrega da OS | até a data da OS | data de entrega − prazo | 1% por dia útil de atraso, até 10% | FICTÍCIO — TR demo 11.1 |
| Defeitos na homologação | 0 defeito crítico | defeitos críticos abertos no aceite | 5% do valor da OS por defeito crítico | FICTÍCIO — TR demo 11.2 |

## 13. Relatórios e evidências

- Relatórios exigidos: abertura, diario, fechamento, semanal, mensal, planejamento (títulos adaptados ao edital).
- Todo dia: abertura, relatório diário e fechamento (Word).
- Por módulo: 15 evidências obrigatórias (escopo, requisitos, arquitetura, código alterado, commits, testes, logs, segurança, preview, capturas, revisões, responsáveis, medição, implantação, aceite).
- Checklist de 100 controles antes de cada entrega.

## 14. Riscos

- ⚠ Perfil ANALISTA_REQUISITOS: sem pessoa no perfil (10 h planejadas, 0 h disponíveis)
- ⚠ Perfil ANALISTA_TESTES: sem pessoa no perfil (18 h planejadas, 0 h disponíveis)
- ⚠ Perfil DESENVOLVEDOR_PLENO: sem pessoa no perfil (40 h planejadas, 0 h disponíveis)
- ⚠ Perfil DESENVOLVEDOR_SENIOR: sem pessoa no perfil (32 h planejadas, 0 h disponíveis)
- ⛔ T-0028: Nenhum profissional informado: capacidade por perfil = 0 e responsáveis 'a cadastrar'

## 15. Comunicação e controle de mudanças

- Canal com o órgão: gestor/fiscal do contrato. Relatórios diários e mensais em Word.
- Mudança de escopo = registro de decisão + nova linha no planejamento + aprovação humana + aditivo quando o contrato exigir.

## 16. ESTIMATIVA × EXECUÇÃO REAL

| Medida | Planejado (ESTIMATIVA) | Comprovado (REAL) | Aceito (REAL) |
|---|---|---|---|
| UST | 109,8 | 80,4 | 0 |
| Saldo do contrato | — | 219,6 (projetado) | 300 (oficial) |

## 17. Pendências para completar este GEC

- Formulário do contrato completo
- Equipe cadastrada (nome e cargo)
- Documento base (empresa e capacidades)

---
Aprovação humana do GEC: **pendente** (responsável técnico e gestor do contrato).
