---
name: ppj
description: PPJ — gera o Planejamento de Projeto Sustentável (identificação, escopo, entregas, equipe, capacidade e saldo, sustentação, sustentabilidade ambiental/social/econômica, riscos, indicadores), com título e seções extras adaptados ao que o edital exigir.
---
# PPJ — PLANEJAMENTO DE PROJETO SUSTENTÁVEL (G04 Planejador GEC)

1. Verifique `EDITAL.yaml`: se o edital pede outro nome (ex.: "Plano de Trabalho") ou seções específicas, ajuste `documentos.ppj.titulo` e `documentos.ppj.secoes_extras` (com orientação e origem).
2. `python3 fabrica/ferramentas/fabrica.py ppj <ID>` → `contratos/<ID>/PPJ.md`.
3. Complete as seções extras e os itens "a preencher" com base no edital e no GEC, citando cláusulas. Não declare conformidade ambiental/certificação sem evidência.
4. Encaminhe para aprovação humana.
