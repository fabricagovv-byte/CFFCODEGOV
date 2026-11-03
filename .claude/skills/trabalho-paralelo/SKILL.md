---
name: trabalho-paralelo
description: Use com 2+ tarefas independentes (sem estado compartilhado) ou quando dois agentes forem mexer em código ao mesmo tempo - despache um agente por domínio e isole com git worktree.
---
# Trabalho paralelo e isolamento

Adaptado de superpowers/dispatching-parallel-agents e using-git-worktrees (MIT) — originais em `fabrica/conhecimento/superpowers/`.

- **Quando:** falhas/tarefas em áreas diferentes (ex.: MOD-201 relatório e MOD-202 relatório, arquivos distintos). **Não** quando uma depende da outra ou tocam os mesmos arquivos.
- **Como:** um agente por domínio, com objetivo, contexto, restrições e formato de retorno claros. Reserve os arquivos no quadro (`--arquivo`).
- **Isolamento:** `git worktree add ../wt-MOD-201 -b os-001-mod-201` (ou `isolation: worktree` no Claude Code). Verifique a base limpa (testes verdes) antes de começar.
- **Integração:** o Tech Lead (E02) junta, roda a suíte completa (verificar-antes-de-concluir) e resolve conflitos.
