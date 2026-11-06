# Relatório Técnico de Execução e Medição — novembro de 2026

## 1. Situação do contrato

O ciclo é: **a empresa executa → o órgão confere e aceita → o órgão paga**. Cada etapa só avança quando a anterior tem registro.

| Etapa | UST | Valor | Situação |
|---|---|---|---|
| Contratado | 12.000 | — | total do contrato |
| Executado | 202,5 | R$ 6.075,00 | entregue, testado e auditado; vai para o aceite do órgão |
| Aceito pelo órgão | 0 | — | próxima etapa: o órgão confere o executado e emite o termo de aceite |
| Pago | 0 | — | depois do aceite (registre em PAGAMENTOS.csv) |
| **Saldo para executar** | **11.797,5** | | contratado − executado |
| ↳ já planejado | 0 | | 0 módulo(s) com data (seção 11) |
| ↳ ainda sem planejamento | 11.797,5 | | precisa de novas demandas/OS do órgão |

Em uma frase: de 12.000 UST contratadas, 202,5 já foram executadas (1,7%); 0 estão planejadas e 11.797,5 ainda não têm demanda.
> OS-FIC-002: Catálogo PROPOSTO-V1 aprovado pelo responsável em 06/11/2026 (R$ 30,00/UST). A regra de medição parcial é PROPOSTA da fábrica e precisa de confirmação. O órgão contratante ainda não enviou contrato nem OS assinada: nada aqui é ACEITO.

## 2. Meta diária

- **Meta de hoje (06/11/2026):** 0 UST — nenhum módulo planejado para hoje.
- **Executado hoje:** 202,5 UST.

Como a meta é calculada: a UST de cada módulo do planejamento é dividida igualmente pelos dias úteis entre a data de início e a de fim; a meta do dia é a soma dos módulos em andamento naquele dia. O executado entra no dia em que o módulo foi medido.

| Dia | Meta (UST) | Executado (UST) | Meta acumulada | Executado acumulado |
|---|---|---|---|---|
| 06/11 (hoje) | 0 | 202,5 | 0 | 202,5 |

## 3. Identificação

| Campo | Informação |
|---|---|
| Órgão | [EXISTE — nome e documentos a enviar pelo responsável] |
| Contrato | FIC-COM-2026-001 (referência fictícia) |
| Objeto | Plataforma Integrada de Comunicação Institucional e Atendimento Digital, 18 módulos do TR (minuta cl. 2) |
| Ordens de serviço | OS-FIC-002 — Correção e endurecimento da base (12 achados do diagnóstico) |
| Sistema(s) | contratos/FIC-COM-2026-001/laboratorio |
| Período | novembro de 2026 (até 06/11/2026) |
| Contratada | V4 Tecnologia Brasil · DigitalGov — CNPJ 24.361.188/0001-61 |
| Responsável técnico | Warley Luciano Costa Gomes |

## 4. Equipe técnica e agentes de IA

Os agentes de IA executam as etapas técnicas; a equipe técnica responde por eles: orienta, revisa e aprova. Participação individual só aparece quando há registro (commit, revisão, ata ou registro do gestor).

| Nome | Função | Responsabilidade | Desde | Participações registradas |
|---|---|---|---|---|
| Jerlian | Programador | — | — | nenhuma ainda |
| Ruan | Programador | — | — | nenhuma ainda |
| Arthur Miguel | Programador | — | — | nenhuma ainda |
| Warley | Programador | — | — | nenhuma ainda |
| Werverton | Programador | — | — | nenhuma ainda |
| João Miguel | Programador | — | — | nenhuma ainda |
| Warley C. | Programador | — | — | nenhuma ainda |

**Etapas da OS-FIC-002 executadas pelos agentes:**

| Etapa | Agente (papel na fábrica) | Resultado | Data | Situação |
|---|---|---|---|---|
| Código (banco, API, telas, testes) | G06/G07/G08 + gerador de cadastros | commits no git (autor: Claude) | 2026-11-06 | concluído |
| Conferência da autorização | G03 Gestor Contratual | — | — | sem registro |
| Execução dos testes | G12 Engenheiro de Testes | — | — | sem registro |
| Registro dos commits | G17 Auditor de Evidências | — | — | sem registro |
| Auditoria das evidências | G17 Auditor de Evidências | — | — | sem registro |
| Medição | G15 Medidor de UST | — | — | sem registro |
| Relatórios | G19 Gerador de Relatórios | — | — | sem registro |
| Checklist de qualidade | G20 Homologador Técnico | — | — | sem registro |
| Pacote de entrega | G20 Homologador Técnico | — | — | sem registro |

## 5. O que foi feito e quanto foi medido

| Módulo | O que foi entregue | Item do contrato | UST executada | Testes |
|---|---|---|---|---|
| MOD-001 — Controle de sessão (TR M01, item 2 de 4) | Banco de dados, Testes automatizados | CAT-M01-SESSAO | 202,5 | 35 ok, 0 falha(s) |
| MOD-002 — Correções de validação e privacidade (M03, M05, M07, M08) | Banco de dados, Testes automatizados | CORRETIVA-SEM-ITEM | 0 | 34 ok, 0 falha(s) |
| MOD-003 — Base técnica — migrações versionadas, cabeçalhos de segurança, dependências | Banco de dados, Testes automatizados | CORRETIVA-SEM-ITEM | 0 | 9 ok, 0 falha(s) |
| MOD-004 — Painel da fábrica — chave de acesso (ferramenta interna) | Testes automatizados | INTERNO-FABRICA | 0 | 12 ok, 0 falha(s) |
| **Total** | | | **202,5** | |

### MOD-001 — Controle de sessão (TR M01, item 2 de 4)

- **Banco de dados:** estrutura e acesso a dados — 2 arquivo(s), 8 linhas.
- **Testes:** 35 executado(s), 0 falha(s) — APROVADO em 2026-11-06 (1 arquivo(s) de teste, 68 linhas).
- **Medição:** item CAT-M01-SESSAO — M01 item 2 de 4: controle de sessão (810 ÷ 4): previsto 202,5, executado **202,5**, aceito 0 UST.
- **Commits:** `532d886` 2026-11-06 MOD-001 MOD-002 MOD-003: sessão revogável, validações, privacidade e migrações (OS-FIC-002); `f823f56` 2026-11-06 fabrica: diagnóstico do pacote DIGITALGOV (contrato fictício FIC-COM-2026-001).
- **Responsável:** equipe técnica (Jerlian, Ruan, Arthur Miguel, Warley, Werverton, João Miguel, Warley C.); revisão individual deste módulo: sem registro.

![MOD-001 — 001_01_apos_sair (preview)](../evidencias/OS-FIC-002/MOD-001/SCREENSHOTS/MOD-001_01_apos_sair.png)

![MOD-001 — 001_02_bloqueio_tentativas (preview)](../evidencias/OS-FIC-002/MOD-001/SCREENSHOTS/MOD-001_02_bloqueio_tentativas.png)

### MOD-002 — Correções de validação e privacidade (M03, M05, M07, M08)

- **Banco de dados:** estrutura e acesso a dados — 2 arquivo(s), 9 linhas.
- **Testes:** 34 executado(s), 0 falha(s) — APROVADO em 2026-11-06 (1 arquivo(s) de teste, 74 linhas).
- **Medição:** item CORRETIVA-SEM-ITEM — Correção de defeito em código preexistente — sem item no catálogo: previsto 0, executado **0**, aceito 0 UST.
- **Commits:** `532d886` 2026-11-06 MOD-001 MOD-002 MOD-003: sessão revogável, validações, privacidade e migrações (OS-FIC-002); `f823f56` 2026-11-06 fabrica: diagnóstico do pacote DIGITALGOV (contrato fictício FIC-COM-2026-001).
- **Responsável:** equipe técnica (Jerlian, Ruan, Arthur Miguel, Warley, Werverton, João Miguel, Warley C.); revisão individual deste módulo: sem registro.

![MOD-002 — 002_01_leitor_so_publicadas (preview)](../evidencias/OS-FIC-002/MOD-002/SCREENSHOTS/MOD-002_01_leitor_so_publicadas.png)

![MOD-002 — 002_02_leitor_chamados (preview)](../evidencias/OS-FIC-002/MOD-002/SCREENSHOTS/MOD-002_02_leitor_chamados.png)

### MOD-003 — Base técnica — migrações versionadas, cabeçalhos de segurança, dependências

- **Banco de dados:** estrutura e acesso a dados — 3 arquivo(s), 34 linhas.
- **Testes:** 9 executado(s), 0 falha(s) — APROVADO em 2026-11-06 (2 arquivo(s) de teste, 113 linhas).
- **Medição:** item CORRETIVA-SEM-ITEM — Correção de defeito em código preexistente — sem item no catálogo: previsto 0, executado **0**, aceito 0 UST.
- **Commits:** `532d886` 2026-11-06 MOD-001 MOD-002 MOD-003: sessão revogável, validações, privacidade e migrações (OS-FIC-002); `f823f56` 2026-11-06 fabrica: diagnóstico do pacote DIGITALGOV (contrato fictício FIC-COM-2026-001).
- **Responsável:** equipe técnica (Jerlian, Ruan, Arthur Miguel, Warley, Werverton, João Miguel, Warley C.); revisão individual deste módulo: sem registro.

### MOD-004 — Painel da fábrica — chave de acesso (ferramenta interna)

- **Testes:** 12 executado(s), 0 falha(s) — APROVADO em 2026-11-06 (3 arquivo(s) de teste, 130 linhas).
- **Medição:** item INTERNO-FABRICA — Ferramenta interna da contratada (painel da fábrica) — não é entregável do contrato: previsto 0, executado **0**, aceito 0 UST.
- **Commits:** `de17ba0` 2026-11-06 MOD-004: painel da fábrica exige chave de acesso (OS-FIC-002); `f823f56` 2026-11-06 fabrica: diagnóstico do pacote DIGITALGOV (contrato fictício FIC-COM-2026-001).
- **Responsável:** equipe técnica (Jerlian, Ruan, Arthur Miguel, Warley, Werverton, João Miguel, Warley C.); revisão individual deste módulo: sem registro.

![MOD-004 — 004_01_pede_chave (preview)](../evidencias/OS-FIC-002/MOD-004/SCREENSHOTS/MOD-004_01_pede_chave.png)

![MOD-004 — 004_02_chave_errada (preview)](../evidencias/OS-FIC-002/MOD-004/SCREENSHOTS/MOD-004_02_chave_errada.png)

## 6. De onde vêm os números (memória de cálculo)

1. **O contrato define o catálogo de serviços** (`CATALOGO_SERVICOS.csv`): para cada serviço, quantas horas de cada perfil ele consome.
2. **A quantidade de cada módulo está definida na OS / tabela do contrato** (`TABELA_UST.csv`).
3. **A fórmula do contrato é `definida na OS`**.
4. **A OS diz quais serviços cada módulo usa.**
5. **O módulo só conta como executado** quando o código está no git, os testes passaram e a auditoria das evidências aprovou. Linhas de código não entram na conta.

| Módulo | Serviço | Conta | UST | Valor |
|---|---|---|---|---|
| MOD-001 | CAT-M01-SESSAO | previsto=202.5 UST (OS OS-FIC-002, item CAT-M01-SESSAO) | 202,5 | R$ 6.075,00 |
| MOD-002 | CORRETIVA-SEM-ITEM | previsto=0 UST (OS OS-FIC-002, item CORRETIVA-SEM-ITEM) | 0 | — |
| MOD-003 | CORRETIVA-SEM-ITEM | previsto=0 UST (OS OS-FIC-002, item CORRETIVA-SEM-ITEM) | 0 | — |
| MOD-004 | INTERNO-FABRICA | previsto=0 UST (OS OS-FIC-002, item INTERNO-FABRICA) | 0 | — |

Exemplo de leitura: "4 h Analista × 1,2" significa 4 horas do perfil Analista, que valem 1,2 UST por hora = 4,8 UST.

## 8. Tecnologias utilizadas

| Camada | Tecnologias | Fonte |
|---|---|---|
| Backend (Python) | fastapi, uvicorn, pytest, httpx, python-docx | `contratos/FIC-COM-2026-001/laboratorio/FABRICA/requirements.txt` |
| Backend (Python) | fastapi, uvicorn, pydantic, httpx, pytest | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/requirements.txt` |

## 9. Código de novembro de 2026

**contratos/FIC-COM-2026-001/laboratorio:** 3 commit(s), +3251 / −82 linhas.

| Camada | Arquivos alterados | Linhas adicionadas | Linhas removidas |
|---|---|---|---|
| Outros | 46 | 2649 | 62 |
| Testes automatizados | 10 | 429 | 6 |
| Documentação | 5 | 89 | 1 |
| Banco de dados | 9 | 84 | 13 |

| Commit | Data | Descrição |
|---|---|---|
| `de17ba0` | 2026-11-06 | MOD-004: painel da fábrica exige chave de acesso (OS-FIC-002) |
| `532d886` | 2026-11-06 | MOD-001 MOD-002 MOD-003: sessão revogável, validações, privacidade e migrações (OS-FIC-002) |
| `f823f56` | 2026-11-06 | fabrica: diagnóstico do pacote DIGITALGOV (contrato fictício FIC-COM-2026-001) |

### Código de hoje (06/11/2026)

**contratos/FIC-COM-2026-001/laboratorio:** 3 commit(s), +3251 / −82 linhas.

| Camada | Arquivos alterados | Linhas adicionadas | Linhas removidas |
|---|---|---|---|
| Outros | 46 | 2649 | 62 |
| Testes automatizados | 10 | 429 | 6 |
| Documentação | 5 | 89 | 1 |
| Banco de dados | 9 | 84 | 13 |

## 10. Código total do sistema

**contratos/FIC-COM-2026-001/laboratorio:** 56 arquivo(s), 3338 linhas, 3 commit(s) desde o início.

| Camada | Arquivos | Linhas |
|---|---|---|
| Outros | 37 | 2756 |
| Testes automatizados | 8 | 423 |
| Documentação | 3 | 88 |
| Banco de dados | 8 | 71 |

| Linguagem | Arquivos | Linhas |
|---|---|---|
| JSON | 4 | 1523 |
| Python | 22 | 1223 |
| Outros | 9 | 338 |
| Markdown | 3 | 88 |
| JavaScript | 4 | 48 |
| YAML | 1 | 40 |
| SQL | 6 | 34 |
| Shell | 1 | 22 |
| Texto | 2 | 10 |
| HTML | 2 | 9 |
| CSS | 2 | 3 |

> Linhas de código e commits mostram o tamanho do trabalho; a quantidade medida vem do catálogo do contrato, não das linhas.

## 11. A fazer (planejado)

Nenhum módulo planejado além do que já foi executado.

## 12. Próximas etapas e pendências

- Próxima etapa normal: enviar ao órgão os 202,5 UST executados para conferência e termo de aceite.
- Registrar a revisão de cada módulo por um membro da equipe (MOD-001, MOD-002, MOD-003, MOD-004) em PARTICIPACOES.csv (data, pessoa, módulo, tipo REVISAO/APROVACAO, evidência).

## 13. Arquivos de origem

- UST: `medicoes/<OS>.json` (medição pelo catálogo do contrato) e `contrato.yaml`.
- O que foi feito, código e commits: repositório git (`git log`, `git ls-files`).
- Testes: `evidencias/<OS>/<MÓDULO>/TESTES.json` (execuções reais com JUnit).
- Telas: capturas reais em `evidencias/<OS>/<MÓDULO>/SCREENSHOTS/`.
- A fazer e meta diária: `PLANEJAMENTO.csv` (estimativa pelo catálogo, datas de início e fim).
- Pagamentos: `PAGAMENTOS.csv` (data, competência, UST, valor e documento do pagamento).

