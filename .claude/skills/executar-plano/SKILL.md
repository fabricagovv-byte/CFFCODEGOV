---
name: executar-plano
description: Use para executar um plano de implementação - tarefa por tarefa, com subagente novo por tarefa quando disponível, revisão em duas etapas (cumpre a especificação? qualidade do código?) e verificação antes de marcar como concluída.
---
# Executar plano (com ou sem subagentes)

Adaptado de superpowers/subagent-driven-development e executing-plans (MIT) — originais em `fabrica/conhecimento/superpowers/`.

Para cada tarefa do plano:
1. Mova no quadro para IN_PROGRESS (a CLI reserva os arquivos e recusa conflito).
2. **Implementador:** subagente do papel (ex.: `e05-dev-backend-1`) com contexto mínimo: tarefa, arquivos, critérios, comando de teste. Sem subagente: faça você mesmo, seguindo tdd.
3. **Revisão 1 — especificação:** o resultado faz exatamente o que a tarefa pede (nem mais, nem menos)?
4. **Revisão 2 — qualidade:** código limpo, erros tratados, segurança (`g13-revisor-codigo`, `g10-seguranca-lgpd`).
5. Problemas → volte ao implementador; não avance com pendência crítica.
6. verificar-antes-de-concluir → commit → mova para DONE com `--resultado` e `--evidencia`.
Dois agentes no mesmo arquivo: use worktree (skill trabalho-paralelo). Nunca confie no "terminei" do subagente sem rodar o teste.
