---
name: rateio-ust
description: RATEIO — divide o total de UST de um dia, semana ou mês entre os profissionais que trabalharam (por área, tipo de participação e senioridade; ou tudo para o sênior da área). Use quando o usuário informar um total (ex.- "a semana fechou 250 UST") ou pedir relatório por profissional.
---
# RATEIO DE UST (G15 Medidor, G18 Profissionais, G19 Relatórios)

1. Confirme o total e a base: aceito (documento do órgão) ou comprovado. Registre em `contratos/<ID>/RATEIO_TOTAIS.csv` (`semanal,<segunda-feira AAAA-MM-DD>,250,aceito,<documento>`).
2. Confirme que `PARTICIPACOES.csv` tem o que cada pessoa fez no período, com prova. Falta registro → pergunte ao usuário; não invente.
3. `python3 fabrica/ferramentas/fabrica.py rateio semanal <ID> --data <AAAA-MM-DD>` (ou diario/mensal). Regra em `RATEIO.yaml` (modo proporcional ou senior_da_area).
4. Gere o relatório do período, que já inclui o rateio: `python3 fabrica/ferramentas/fabrica.py relatorio semanal <ID> --data <AAAA-MM-DD>`; por pessoa: `python3 fabrica/ferramentas/fabrica.py relatorio profissional <ID> --profissional P01 --data <AAAA-MM-01>`.
5. Ao responder, diga a regra usada, a base do total e que é divisão interna (não muda a medição do contrato).
