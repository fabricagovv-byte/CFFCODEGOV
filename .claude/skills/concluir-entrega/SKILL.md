---
name: concluir-entrega
description: Use quando a implementação de um módulo/OS terminou e os testes passam - verifique tudo, decida como integrar (PR, merge, manter branch) e prepare a entrega com evidências.
---
# Concluir a entrega

Adaptado de superpowers/finishing-a-development-branch (MIT) — original em `fabrica/conhecimento/superpowers/finishing-a-development-branch/SKILL.md`.

1. Suíte completa verde (verificar-antes-de-concluir): backend, frontend, `alembic check`, build.
2. `python3 fabrica/ferramentas/fabrica.py fluxo <C> <OS>` — roda testes → commits → auditoria → medição → relatórios → checklist e **pausa** se faltar verificação humana.
3. Ofereça ao usuário: abrir PR (só se ele pedir), integrar na branch principal, ou manter a branch. Nunca force push em branch alheia.
4. Após aprovação humana registrada: `python3 fabrica/ferramentas/fabrica.py fluxo <C> <OS> --aprovado-por "Nome (cargo)"` → pacote de entrega.
5. Limpe worktrees usados.
