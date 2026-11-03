---
name: plano-implementacao
description: Use quando houver especificação ou requisitos de uma tarefa com vários passos, antes de mexer no código - escreva um plano com arquivos exatos, passos de 2-5 minutos, testes e comandos de verificação.
---
# Plano de implementação

Adaptado de superpowers/writing-plans (MIT) — original em `fabrica/conhecimento/superpowers/writing-plans/SKILL.md`.

Salve em `contratos/<ID>/especificacoes/<MOD>/plano-implementacao.md`:
- **Cabeçalho:** objetivo, arquitetura em 2 linhas, stack, requisitos do edital cobertos (IDs), restrições globais (AGENTS.md).
- **Estrutura de arquivos:** o que criar/alterar, com caminho.
- **Tarefas pequenas** (2–5 min cada), cada uma com: arquivos, teste a escrever primeiro, código esperado, comando para rodar e resultado esperado, commit (`MOD-NNN: ...`).
- **Ordem e dependências**; marque com [P] o que pode rodar em paralelo (arquivos diferentes).
- Crie as tarefas no quadro: `python3 fabrica/ferramentas/fabrica.py tarefas criar --agente <ID> --modulo <MOD> --arquivo <caminho> ...`.
Depois: skill executar-plano.
