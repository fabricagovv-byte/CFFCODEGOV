---
name: especificar-modulo
description: Use antes de desenvolver um módulo a partir de exigências do edital - especificação orientada (Spec-Driven Development) - spec com histórias e critérios de aceite, esclarecimentos, plano técnico, tarefas e análise de consistência, tudo rastreado às cláusulas.
---
# Especificar módulo (Spec-Driven Development)

Adaptado de github/spec-kit (MIT) — método em `fabrica/conhecimento/spec-kit/spec-driven.md`, modelos em `fabrica/conhecimento/spec-kit/templates/`.

Pasta: `contratos/<ID>/especificacoes/<MOD>/`

1. **Constituição** = `AGENTS.md` (regras inegociáveis). Toda decisão passa por ela.
2. **spec.md** (o quê e por quê, sem tecnologia): histórias de usuário priorizadas (P1, P2…), cada uma testável sozinha, com cenários **Dado / Quando / Então**; requisitos funcionais `RF-001…` com a cláusula do edital; critérios de sucesso mensuráveis; **[PRECISA ESCLARECER: …]** onde o edital é omisso (no máximo 3, as mais importantes).
3. **Esclarecer:** pergunte ao usuário só os [PRECISA ESCLARECER]; registre respostas na spec e em `python3 fabrica/ferramentas/fabrica.py decisao`.
4. **plano.md** (como): contexto técnico, stack do contrato, modelo de dados, contratos de API, checagem contra a constituição (segurança, LGPD, acessibilidade, testes).
5. **tarefas.md:** por história (P1 primeiro), testes antes do código, [P] para paralelizáveis, caminhos exatos → quadro de tarefas.
6. **Analisar:** consistência spec × plano × tarefas × edital (requisito sem tarefa? tarefa sem requisito?). Corrija antes de codar.
7. Cadastros simples: a especificação de entidade alimenta `python3 fabrica/ferramentas/fabrica.py crud gerar`.
