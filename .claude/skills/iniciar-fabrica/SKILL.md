---
name: iniciar-fabrica
description: INICIAR FÁBRICA / INICIAR EQUIPE — carrega a configuração, verifica os 44 agentes, skills, quadro de comunicação e ferramentas do ambiente. Use no começo de cada sessão.
---
# INICIAR FÁBRICA

1. Rode `python3 fabrica/ferramentas/fabrica.py agentes gerar` (regenera .claude/agents a partir de fabrica/agentes/registry.yaml) e `python3 fabrica/ferramentas/fabrica.py iniciar`.
2. Rode `python3 fabrica/ferramentas/fabrica.py painel` e `python3 fabrica/ferramentas/fabrica.py tarefas validar`.
3. Liste as skills externas que o usuário forneceu (pasta indicada por ele). Não pesquise nem instale skills externas.
4. Apresente: o que está OK, o que está PENDENTE (com o motivo real da CLI) e as próximas ações.
5. Não declare nada como verificado sem a saída do comando.
