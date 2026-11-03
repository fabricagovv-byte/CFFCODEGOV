# CLAUDE.md

As instruções gerais da fábrica estão em AGENTS.md (compartilhadas com o Codex) e são importadas aqui:

@AGENTS.md

## Específico do Claude Code

- **Início de sessão:** se o usuário não fez um pedido específico, rode a skill `/proximo-passo` e diga o que falta e a próxima ação.
- **Agentes:** `.claude/agents/*.md` (44 subagentes) são **gerados** de `fabrica/agentes/registry.yaml` com
  `python3 fabrica/ferramentas/fabrica.py agentes gerar`. Edite o registro, não os arquivos gerados. Depois de gerar,
  reinicie a sessão (ou use `/agents`) para o Claude Code recarregar.
- **Delegação:** para tarefas paralelas, delegue ao subagente do papel (ex.: `g13-revisor-codigo` para revisão independente,
  `g10-seguranca-lgpd` para segurança). Antes de delegar, crie a tarefa no quadro com `--arquivo` para reservar os arquivos.
  Use `isolation: worktree` quando dois agentes forem alterar código ao mesmo tempo.
- **Comandos:** as skills em `.claude/skills/` respondem como `/iniciar-fabrica`, `/novo-contrato`, `/executar-os`, `/medir-producao`,
  `/relatorio-diario`, `/preparar-entrega` etc. `/publicar-producao` só pode ser chamada pelo usuário.
- **Revisões nativas:** quando disponíveis, use `/code-review` (G13) e `/security-review` (G10) e registre o resultado em `REVISOES.md`/`SEGURANCA.md`.
- **Permissões:** `.claude/settings.json` libera comandos de leitura/teste e bloqueia leitura de `.env` e publicação; não amplie sem pedido do usuário.
- **Sessões na nuvem:** o ambiente é descartável; faça commit e push do que precisar ser preservado (estado do quadro, evidências, relatórios).
