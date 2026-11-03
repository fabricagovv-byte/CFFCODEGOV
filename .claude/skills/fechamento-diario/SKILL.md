---
name: fechamento-diario
description: FECHAMENTO DO DIA — para cada projeto/contrato, consolida quem trabalhou (nomes), produção do dia (commits, tarefas, testes, UST informada), divisão por profissional, acumulados e saldo do contrato; e o consolidado de todos os projetos.
---
# FECHAMENTO DO DIA (G19, G15, G03)

1. Se o usuário informar a produção do dia (ex.: "hoje fechou 40 UST"), registre em `RATEIO_TOTAIS.csv`: `diario,<AAAA-MM-DD>,40,<aceito|comprovado>,<documento ou "registro do gestor">`.
2. Confirme as participações do dia em `PARTICIPACOES.csv` (quem fez o quê, com prova). Sem registro → "sem participação registrada"; não invente.
3. `python3 fabrica/ferramentas/fabrica.py fechamento <ID> --data <AAAA-MM-DD>` → `relatorios/fechamentos/<data>.md` (título adaptável no EDITAL.yaml).
4. Saldo: `python3 fabrica/ferramentas/fabrica.py saldo <ID>` (contratado − aceito = oficial; contratado − comprovado = projetado; média diária e dias até esgotar).
5. Vários projetos (um repositório cada): `python3 fabrica/ferramentas/fabrica.py portfolio <repo1> <repo2> ... --data <AAAA-MM-DD> --saida PORTFOLIO.md`.
6. Resuma ao usuário: quem trabalhou, produção do dia, saldo.
