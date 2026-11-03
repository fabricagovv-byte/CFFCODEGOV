---
name: configurar-fabrica
description: CONFIGURAR FÁBRICA — ajuda o usuário a preencher a configuração central (empresa, fuso, jornada, feriados, produtividade, relatórios, rateio, stacks, limites) e valida.
---
# Configurar a fábrica

1. Mostre a configuração: `python3 fabrica/ferramentas/fabrica.py config mostrar` (arquivo `fabrica/CONFIGURACAO_FABRICA.yaml`).
2. Pergunte só o que falta, em linguagem simples (ex.: "quantas horas por dia a equipe trabalha?", "feriados do município?", "produtividade em horas por PF do contrato?").
3. Edite o arquivo e valide: `python3 fabrica/ferramentas/fabrica.py config verificar`.
4. Limites (o que a IA nunca faz sozinha) só podem ficar **mais** restritivos sem decisão do responsável.
