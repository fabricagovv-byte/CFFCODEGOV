# Repositório de sistema — Fábrica de Software Governamental

Um repositório = **um sistema** (ver `PROJETO.yaml`). A configuração da fábrica (agentes, comandos, regras) já vem pronta.

## Primeiros passos

1. Abra este repositório no Claude Code (app, web ou terminal) ou no Codex.
2. Diga **"INICIAR FÁBRICA"**.
3. Envie a planilha preenchida (`PLANILHA_PREENCHIMENTO.xlsx`) e os documentos do contrato e diga **"IMPORTAR PLANILHA <ID-do-contrato>"** e **"NOVO CONTRATO <ID>"**.
4. Siga `fabrica/docs/COMO_INICIAR.md`.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `PROJETO.yaml` | identidade do sistema e componentes (stacks) |
| `projetos/<sistema>/` | código-fonte |
| `contratos/<ID>/` | contrato, OS, evidências, medições, rateios, relatórios, entregas |
| `fabrica/` | ferramentas, agentes, modelos, guias (não editar sem necessidade) |
| `AGENTS.md` / `CLAUDE.md` | regras para Codex / Claude Code |

Verificar tudo: `python3 fabrica/ferramentas/fabrica.py iniciar && python3 fabrica/ferramentas/fabrica.py projeto verificar --instalar`.
