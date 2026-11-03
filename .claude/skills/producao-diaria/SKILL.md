---
name: producao-diaria
description: Workflow de produção automática diária — lê tarefas pendentes, verifica autorizações e bloqueios, executa o que está autorizado, testa, revisa, registra evidências, mede, gera relatório e prepara o próximo dia. Use em execuções agendadas.
---
# PRODUÇÃO DIÁRIA

1. `python3 fabrica/ferramentas/fabrica.py iniciar` e `python3 fabrica/ferramentas/fabrica.py painel`.
2. `python3 fabrica/ferramentas/fabrica.py tarefas listar --status READY` e `--status BLOCKED`. Para cada OS com tarefas, verifique a autorização no YAML; OS sem autorização: só planejamento, nada de código.
3. Execute as tarefas READY autorizadas (skill executar-os), respeitando dependências e reservas de arquivos.
4. `python3 fabrica/ferramentas/fabrica.py testes executar` → `python3 fabrica/ferramentas/fabrica.py evidencias commits` → `python3 fabrica/ferramentas/fabrica.py auditar` → `python3 fabrica/ferramentas/fabrica.py medir` para cada OS trabalhada.
5. `python3 fabrica/ferramentas/fabrica.py relatorio diario <C>` e `python3 fabrica/ferramentas/fabrica.py fechamento <C>` para cada contrato trabalhado (relatórios exigidos pelo edital: ver EDITAL.yaml `relatorios_exigidos`).
6. Atualize o cronograma do GEC se houver atraso; crie as tarefas do dia seguinte.
7. Commit e push na branch de trabalho. Nunca publique em produção nesta rotina.

O agendamento depende do ambiente (Claude Code: /loop ou Routines; Codex: automação própria; servidor: cron com `claude -p`). Credenciais e permissões precisam ser configuradas pelo usuário.
