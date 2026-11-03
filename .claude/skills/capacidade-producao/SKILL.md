---
name: capacidade-producao
description: QUANTO EU PRODUZO / CAPACIDADE — estima a produção da equipe por pessoa, dia e mês em UST, PF, horas e valor, a partir da jornada, dos perfis do contrato e da produtividade informada; compara com o histórico aceito. Sempre rotulado como estimativa.
---
# Capacidade e estimativa de produção

1. Equipe real: `python3 fabrica/ferramentas/fabrica.py capacidade <ID>`. Sem equipe ainda: `python3 fabrica/ferramentas/fabrica.py capacidade <ID> --simular "DESENVOLVEDOR_PLENO=3,ANALISTA_TESTES=1"`.
2. Premissas em `fabrica/CONFIGURACAO_FABRICA.yaml`: horas/dia, aproveitamento, feriados, `produtividade_horas_por_pf`; fatores e valor/hora em `PERFIS.csv`.
3. Responda com os números **e as premissas**, deixando claro: estimativa ≠ medição ≠ aceite. Se houver PRODUCAO_HISTORICA.csv, mostre a comparação com o real.
