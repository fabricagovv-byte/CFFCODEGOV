# AGENTS.md — Fábrica de Software Governamental

Instruções permanentes para agentes de código (OpenAI Codex, Claude Code e compatíveis) neste repositório.
Idioma de trabalho: **português do Brasil**.

## O que é este repositório

Uma fábrica de software para contratos públicos de TI (desenvolvimento, manutenção, sustentação). Ela organiza
40 agentes de IA (20 da Fábrica Governamental `G01–G20` + 20 do time de Engenharia `E01–E20`), profissionais
humanos reais, contratos, ordens de serviço (OS), evidências, medição (UST/PF), relatórios e entregas.

| Pasta | Conteúdo |
|---|---|
| `fabrica/agentes/registry.yaml` | **Fonte única** dos 40 agentes (função, responsabilidades, ferramentas, comunicação) |
| `fabrica/docs/EQUIPE_AGENTES.md` | Tabela da equipe (gerada) |
| `fabrica/ferramentas/fabrica.py` | CLI: quadro de tarefas, mensagens, evidências, testes, auditoria, medição, checklist, relatórios, entrega |
| `fabrica/comunicacao/` | `AGENT_TASKS.json`, `AGENT_MESSAGES.jsonl`, `AGENT_DECISIONS.md`, `AGENT_HANDOFFS.md`, `AGENT_BLOCKERS.md` |
| `fabrica/qualidade/checklist_100.yaml` | 100 controles de qualidade (10 grupos × 10) |
| `fabrica/templates/` | Formulário do contrato, CSVs (profissionais, participações, tabela UST, produção histórica), GEC, modelos de evidência |
| `fabrica/docs/` | Guias: passo a passo, o que enviar, medição UST, linguagens |
| `fabrica/legislacao/REFERENCIAS.md` | Leis e normas de referência e como verificar aplicabilidade |
| `contratos/<ID>/` | Um contrato: formulário, matriz, GEC, OS, evidências, medições, relatórios, checklist, entregas |
| `projetos/<nome>/` | Código-fonte dos sistemas |
| `PROJETO.yaml` | Identidade do repositório: um repositório = um sistema; componentes e stacks |
| `fabrica/stacks/` | Perfis e esqueletos por linguagem (Python, TypeScript/React/Node, Java, C#, PHP, Go, Rust) + `VERIFICACAO.md` |
| `fabrica/modelos_repositorio/` | README, CI, .gitignore e PROJETO.yaml usados ao criar repositórios novos |
| `.claude/agents/`, `.claude/skills/` | Agentes e comandos no formato do Claude Code (gerados/definidos aqui) |

## Regras inegociáveis

1. **Nada inventado.** Commits vêm do `git`; testes, de execuções reais (JUnit/log); participação humana, horas, revisões, aprovações e aceites, somente de registros preenchidos por pessoas. Sem registro = "sem registro".
2. **Diferencie** PLANEJADO, INICIADO, EXECUTADO, VERIFICADO e ACEITO. Aprovação técnica automatizada **não** é aceite do contratante.
3. **UST ≠ PF ≠ horas.** Não converta sem fórmula escrita no contrato (`medicao.formula` + `PERFIS.csv` + `CATALOGO_SERVICOS.csv`). Linhas de código não comprovam quantidade faturável.
4. **Autorização:** não execute OS sem `autorizacao.autorizado: true` + `autorizado_por` + `data` no YAML da OS. Não publique em produção sem `pode_publicar_producao: true` e confirmação humana na conversa.
5. **Skills externas** são fornecidas pelo usuário. Não pesquise nem instale skills externas por conta própria.
6. **Segurança desde a concepção:** sem segredos no git (`.env` fora do versionamento), menor privilégio, auditoria, dados fictícios em demonstrações, LGPD.
7. **Documentos contratuais primeiro:** leia edital/TR/contrato antes de planejar; cite cláusula/página; conflitos vão para análise humana.
8. **Legislação:** verifique o ente, o regime e a data antes de afirmar aplicabilidade (ver `fabrica/legislacao/REFERENCIAS.md`). Não declare certificação/conformidade integral sem evidência.
9. **Dados pessoais da equipe (CPF):** CPF completo só em `contratos/<ID>/privado/` (no `.gitignore`, permissão 600), importado por `fabrica.py profissionais importar`. Em arquivos versionados, relatórios e mensagens use apenas `cpf_mascarado`. Nunca imprima, faça commit ou envie CPF completo.
10. **Rateio é interno:** dividir o total de UST do período entre profissionais (`fabrica.py rateio`) só considera quem tem participação registrada no período; mostre sempre a regra, a base do total e o documento. Rateio não altera medição nem aceite.
11. **Sem assinatura:** aceite pode vir de qualquer documento do órgão (termo, ofício, e-mail do fiscal). Sem documento do órgão, a quantidade fica COMPROVADA, nunca ACEITA. Participação humana sem assinatura usa a prova disponível (commit, PR, ata, "registro do gestor em data") — e o relatório mostra qual foi.
12. **Um repositório por sistema:** todo repositório novo nasce do modelo (`fabrica.py repositorio novo` ou `CONFIGURACAO_FABRICA.zip`), com `PROJETO.yaml`, stack declarada e CI. Veja `fabrica/docs/PADRAO_REPOSITORIOS.md`.
13. **Linguagem nova:** antes de usar uma stack sem perfil, crie `fabrica/stacks/<id>.yaml` + esqueleto com teste e rode `fabrica.py stacks verificar <id>`. Stack não verificada é declarada como tal.
14. **O edital manda:** exigências e adaptações ficam em `contratos/<ID>/EDITAL.yaml` (títulos de documentos, seções obrigatórias, relatórios exigidos, unidade de medição, equipe, tecnologias). Se o edital pede diferente do padrão, mude ali — os geradores (PPJ, fechamento, relatórios) seguem. Depois rode `fabrica.py edital confrontar <ID>` e diga ao usuário o que atende, o que ajustar e o que falta.
15. **Cadastro mínimo da equipe:** basta nome e função (`fabrica.py profissionais adicionar` ou aba PROFISSIONAIS do documento base). Os demais campos melhoram o confronto com o edital e o rateio.
16. **Documentos em Word:** todo relatório, fechamento, PPJ, confronto, medição, checklist, auditoria e oportunidades sai em `.md` e `.docx` (capa, cabeçalho, rodapé com páginas, tabelas formatadas) via `fabrica/ferramentas/word.cjs`. Requer Node.js + `npm install --prefix fabrica/ferramentas`. Para converter qualquer `.md`: `fabrica.py word <arquivo>`.
17. **Aumentar a produção só com trabalho real:** para "gerar mais UST", use `fabrica.py oportunidades` (trabalho comprovado que pode corresponder a itens do catálogo ainda não medidos), mais capacidade e menos retrabalho. Nunca aumente quantidades sem trabalho executado, sem enquadramento no catálogo ou com dupla contagem.
18. **O planejamento é do responsável:** o usuário define projetos, módulos, serviços, datas e responsáveis (PLANEJAMENTO.csv / aba PLANEJAMENTO). A fábrica calcula, alerta (capacidade, saldo, prazos do edital) e gera as OS; sempre releia o edital ao planejar.
19. **Três relatórios por dia:** abertura (`fabrica.py abertura`), relatório diário (`relatorio diario`) e fechamento (`fechamento`), todos em Word.
20. **Código real e completo:** cadastro = tabela + migração + API validada + auditoria + permissão + tela + testes de API e de tela, separado por módulo (`fabrica.py crud gerar`), provado com testes no PostgreSQL, `alembic check` e build. Sem teste executado, não há entrega.

## Como os agentes trabalham juntos

- Toda atividade é uma tarefa no quadro, criada/movida **pela CLI** (nunca edite o JSON à mão):
  `python3 fabrica/ferramentas/fabrica.py tarefas criar|mover|listar|validar`.
- Estados: `BACKLOG → READY → IN_PROGRESS → IN_REVIEW → TESTING → DONE`, com `BLOCKED` a partir de qualquer estado ativo.
  A CLI recusa: dependência não concluída, **arquivo reservado por outra tarefa IN_PROGRESS** (evita conflito), bloqueio sem motivo, DONE sem resultado/evidência existente.
- Comunicação: `fabrica.py msg`, `decisao`, `handoff`, `bloqueio` (gravam nos arquivos de `fabrica/comunicacao/`).
- Dois agentes no mesmo arquivo ao mesmo tempo: use branches ou `git worktree` separados e integre pelo Tech Lead (E02).
- Fluxo hierárquico: G01 Diretor recebe → G02 lê o edital → G04 planeja (GEC) → G05/E03 arquitetura → E02 Tech Lead quebra em tarefas → E04/E08 distribuem → devs implementam → G12/G13/G10 verificam → G17 audita → G15/G16 medem → G19 relata → G20 prepara homologação → **humano aprova**.

## Fluxo obrigatório por módulo (15 passos)

1 requisitos → 2 arquitetura → 3 tarefas → 4 distribuição → 5 código → 6 integração → 7 testes → 8 correções →
9 revisão de código → 10 segurança → 11 commits → 12 documentação → 13 preview → 14 evidências → 15 aprovação humana.

Evidências obrigatórias por módulo em `contratos/<C>/evidencias/<OS>/<MOD>/`:
`ESCOPO.md REQUISITOS.md ARQUITETURA.md CODIGO_ALTERADO.md COMMITS.json TESTES.json LOGS_TESTES/ SEGURANCA.md PREVIEW.md SCREENSHOTS/ REVISOES.md RESPONSAVEIS.md MEDICAO.md IMPLANTACAO.md ACEITE.md`.

## Comandos operacionais

Cada comando tem uma skill em `.claude/skills/<nome>/SKILL.md` (Codex: leia o arquivo correspondente e siga-o).

| Comando | Skill | Principais chamadas da CLI |
|---|---|---|
| INICIAR FÁBRICA / INICIAR EQUIPE | `iniciar-fabrica` | `agentes gerar`, `iniciar`, `painel` |
| NOVO CONTRATO | `novo-contrato` (+ `analisar-edital`) | `contrato novo`, `contrato faltantes` |
| PLANEJAR CONTRATO / PLANEJAR PROJETO | `planejar-contrato` | `tarefas criar`, `tarefas validar` |
| EXECUTAR OS / INICIAR DESENVOLVIMENTO | `executar-os` | `tarefas mover`, `testes executar` |
| VERIFICAR CÓDIGO / REVISAR CÓDIGO / EXECUTAR TESTES | `verificar-codigo` | `testes executar` |
| AUDITAR EVIDÊNCIAS / AUDITAR MÓDULO | `auditar-evidencias` | `evidencias commits`, `auditar` |
| MEDIR PRODUÇÃO | `medir-producao` | `medir`, `producao estatisticas` |
| RELATÓRIO DIÁRIO / GERAR RELATÓRIO | `relatorio-diario` | `relatorio diario|semanal|mensal|profissional` |
| GERAR PREVIEW | `gerar-preview` | `node fabrica/ferramentas/capturar_telas.cjs` |
| PREPARAR ENTREGA | `preparar-entrega` | `checklist`, `entrega` |
| PREPARAR PUBLICAÇÃO | `preparar-publicacao` | — (manual de publicação do projeto) |
| PUBLICAR PRODUÇÃO | `publicar-producao` | exige autorização humana |
| IMPORTAR PLANILHA / DOCUMENTO BASE | `importar-planilha` | `planilha importar`, `profissionais importar` |
| RATEIO (diário/semanal/mensal) | `rateio-ust` | `rateio`, `relatorio ... --total-ust` |
| NOVO REPOSITÓRIO / NOVO SISTEMA | `novo-repositorio` | `repositorio novo|lote`, `stacks listar`, `projeto verificar` |
| CONFRONTAR EDITAL | `confrontar-edital` | `edital confrontar` |
| FECHAMENTO DO DIA / SALDO | `fechamento-diario` | `fechamento`, `saldo`, `portfolio --data` |
| PPJ (Planejamento de Projeto Sustentável) | `ppj` | `ppj` |
| IMPORTAR EQUIPE / DOCUMENTO DA EQUIPE (Nome, CPF, Cargo) | `importar-planilha` | `profissionais modelo|importar|oficial` |
| OPORTUNIDADES DE MEDIÇÃO | `medir-producao` | `oportunidades` |
| ABERTURA DO DIA | `abertura-dia` | `abertura` |
| PLANEJAMENTO (por projeto) | `planejamento-projetos` | `planejamento consolidar|gerar-os` |
| GERAR CRUD / CADASTRO | `gerar-crud` | `crud gerar` |
| Produção diária automática | `producao-diaria` | todas as anteriores, sem publicar |

## Verificações antes de concluir qualquer trabalho

```bash
python3 fabrica/ferramentas/fabrica.py iniciar
python3 -m pytest fabrica/ferramentas/tests -q
python3 fabrica/ferramentas/fabrica.py projeto verificar --instalar   # testa todos os componentes do PROJETO.yaml
python3 fabrica/ferramentas/fabrica.py tarefas validar
```

## Padrões de código

Código limpo e modular; tipagem (type hints / TypeScript strict); tratamento de erros explícito; testes automatizados por módulo
(nome `test_modNNN_*.py` / `*.test.tsx`); migrações versionadas; logs sem dados pessoais desnecessários; acessibilidade (rótulos, foco,
contraste, `role=alert`); configuração por variáveis de ambiente; mensagens de commit no formato `MOD-NNN: descrição` ou `fabrica: descrição`.
Stack padrão quando o contrato não exigir outra: ver `fabrica/docs/LINGUAGENS.md`.
