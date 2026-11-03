---
name: criar-skill
description: Use para criar ou melhorar uma skill (comando) da fábrica - quando um trabalho se repete, escreva a skill, teste com um caso real e só então publique.
---
# Criar skill da fábrica

Adaptado de anthropics/skills skill-creator (Apache 2.0) e superpowers/writing-skills (MIT) — originais em `fabrica/conhecimento/`.

1. **Quando:** o mesmo procedimento já foi feito 2+ vezes ou o usuário pede um comando novo.
2. **Teste primeiro:** descreva um cenário real e o resultado esperado; rode sem a skill e anote onde falhou.
3. **Escreva** `.claude/skills/<nome>/SKILL.md`: `name`, `description` dizendo **quando usar** (gatilhos em português), passos numerados, comandos da CLI, regras do AGENTS.md que se aplicam. Curta e direta; detalhes em arquivos de referência.
4. **Teste com a skill** no mesmo cenário; ajuste até passar.
5. Registre na tabela de comandos do `AGENTS.md`, gere os agentes (`python3 fabrica/ferramentas/fabrica.py agentes gerar`) e confira `python3 fabrica/ferramentas/fabrica.py iniciar`.
