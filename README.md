# CFFCODEGOV — Fábrica de Software Governamental com IA

Estrutura para executar contratos públicos de software com **40 agentes de IA** (Claude Code e Codex),
**profissionais humanos reais**, evidências verificáveis, medição por UST/PF e entregas mensais.

## Comece por aqui

| Quero… | Abra |
|---|---|
| **Começar um sistema novo (repositório próprio)** | [fabrica/docs/COMO_INICIAR.md](fabrica/docs/COMO_INICIAR.md) |
| Padrão para muitos projetos (ex.: 30) | [fabrica/docs/PADRAO_REPOSITORIOS.md](fabrica/docs/PADRAO_REPOSITORIOS.md) |
| Preencher a planilha (equipe, CPF, rateio, projetos) | [fabrica/docs/PREENCHIMENTO_LEIA-ME.md](fabrica/docs/PREENCHIMENTO_LEIA-ME.md) |
| Linguagens com esqueleto testado | [fabrica/stacks/VERIFICACAO.md](fabrica/stacks/VERIFICACAO.md) |
| Saber o que enviar e o que preencher | [fabrica/docs/O_QUE_ENVIAR.md](fabrica/docs/O_QUE_ENVIAR.md) |
| O passo a passo completo | [fabrica/docs/GUIA_PASSO_A_PASSO.md](fabrica/docs/GUIA_PASSO_A_PASSO.md) |
| Ver a equipe (agentes) | [fabrica/docs/EQUIPE_AGENTES.md](fabrica/docs/EQUIPE_AGENTES.md) |
| Entender a medição (UST, PF, por profissional) | [fabrica/docs/MEDICAO_UST.md](fabrica/docs/MEDICAO_UST.md) |
| Linguagens suportadas | [fabrica/docs/LINGUAGENS.md](fabrica/docs/LINGUAGENS.md) |
| Legislação de referência | [fabrica/legislacao/REFERENCIAS.md](fabrica/legislacao/REFERENCIAS.md) |
| Regras para os agentes | [AGENTS.md](AGENTS.md) (Codex) · [CLAUDE.md](CLAUDE.md) (Claude Code) |
| O sistema de teste (TESTE-001) | [projetos/gestao-documental/README.md](projetos/gestao-documental/README.md) |
| Evidências, medição e relatório do teste | [contratos/TESTE-001/](contratos/TESTE-001/) |

## Comandos (diga na conversa)

`INICIAR FÁBRICA` · `NOVO CONTRATO` · `PLANEJAR CONTRATO` · `EXECUTAR OS` · `VERIFICAR CÓDIGO` · `AUDITAR EVIDÊNCIAS` ·
`MEDIR PRODUÇÃO` · `RATEIO` · `IMPORTAR PLANILHA` · `NOVO REPOSITÓRIO` · `RELATÓRIO DIÁRIO` · `GERAR PREVIEW` · `PREPARAR ENTREGA` · `PREPARAR PUBLICAÇÃO` · `PUBLICAR PRODUÇÃO`

Ou pela CLI: `python3 fabrica/ferramentas/fabrica.py --help` (requer Python 3.11+ e PyYAML).

> Este repositório é a **origem** da fábrica e guarda o exemplo TESTE-001. Sistemas reais devem ser criados em repositórios próprios (`CONFIGURACAO_FABRICA.zip` ou `fabrica.py repositorio novo`).
