---
name: relatorio-diario
description: RELATÓRIO DIÁRIO / GERAR RELATÓRIO — consolida o que foi realmente produzido (git, quadro, testes, evidências, medição, participação humana) em relatório diário, semanal, mensal ou por profissional.
---
# RELATÓRIO (G19)

- Diário: `python3 fabrica/ferramentas/fabrica.py relatorio diario <C> [--data AAAA-MM-DD]`
- Semanal: `python3 fabrica/ferramentas/fabrica.py relatorio semanal <C> --data <qualquer dia da semana>`
- Mensal (entrega/conferência do mês): `python3 fabrica/ferramentas/fabrica.py relatorio mensal <C> --data AAAA-MM-01`
- Por profissional: `python3 fabrica/ferramentas/fabrica.py relatorio profissional <C> --profissional P01 --data AAAA-MM-01`

Depois de gerar, leia o arquivo e escreva no topo um resumo executivo de 3–5 linhas sem acrescentar fatos que não estejam no relatório. Diferencie planejado, iniciado, executado, verificado e aceito.
