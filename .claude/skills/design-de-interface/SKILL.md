---
name: design-de-interface
description: Use ao criar ou revisar telas e componentes de sistemas públicos - interfaces claras, acessíveis (WCAG/eMAG), consistentes, responsivas e com boa hierarquia visual, evitando visual genérico.
---
# Design de interface

Adaptado de anthropics/skills frontend-design (Apache 2.0) — original em `fabrica/conhecimento/anthropic-skills/frontend-design/`.

- Comece pelo usuário e pela tarefa (servidor, cidadão, gestor): o que ele precisa fazer em 3 cliques?
- Hierarquia: título claro, ação principal destacada, filtros acima da lista, mensagens perto do campo.
- Acessibilidade obrigatória: rótulos em todos os campos, foco visível, contraste, `role=alert` em erros, navegação por teclado, textos em português simples.
- Consistência: mesmos componentes (Alerta, Paginação, tabela) em todo o sistema; tokens de cor; tema claro/escuro.
- Responsivo: celular (390 px) sem rolagem horizontal; tabelas com rolagem própria.
- Prove com capturas (skill testar-webapp) e testes de tela.
