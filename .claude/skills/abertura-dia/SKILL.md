---
name: abertura-dia
description: ABERTURA DO DIA — primeiro dos 3 relatórios diários (abertura, diário, fechamento) - quanto foi contratado, consumido e o saldo; equipe contratada; o que está planejado para hoje por projeto/módulo com meta do dia em UST e horas; tarefas e bloqueios.
---
# ABERTURA DO DIA (G01 Diretor, G04, G14)

1. `python3 fabrica/ferramentas/fabrica.py abertura <ID> --data <AAAA-MM-DD>` → `relatorios/aberturas/<data>.md` + Word.
2. Leia e diga ao usuário em 4 linhas: saldo, quem está na equipe, o que está planejado hoje (meta em UST/horas), bloqueios.
3. Ciclo do dia: **abertura** (manhã) → execução (executar-os) → **relatório diário** (`python3 fabrica/ferramentas/fabrica.py relatorio diario <ID>`) → **fechamento** (`python3 fabrica/ferramentas/fabrica.py fechamento <ID>`).
