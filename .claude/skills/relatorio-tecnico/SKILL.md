---
name: relatorio-tecnico
description: RELATÓRIO TÉCNICO / RELATÓRIO PARA O ÓRGÃO / MEDIÇÃO DO DIA / META DIÁRIA — um único relatório organizado no papel timbrado - ciclo executado → aceito → pago, saldo para executar (planejado e sem planejamento), meta diária e ritmo até o fim da vigência, memória de cálculo (horas × fator do catálogo); o que foi feito em cada módulo (banco, API, telas, testes) e em qual item do contrato; tecnologias; código do dia, do mês e total; telas; pendências; assinatura.
---
# RELATÓRIO TÉCNICO (G19 + G15)

1. `python3 fabrica/ferramentas/fabrica.py relatorio tecnico <C> [--data AAAA-MM-DD]`
   Gera `contratos/<C>/relatorios/RELATORIO_TECNICO_<data>.md`, `.docx` (papel timbrado de `empresa.papel_timbrado`) e `.json`.
2. Não pergunte nada ao usuário se os dados existem: gere e entregue o `.docx` (SendUserFile) com um resumo de 3 linhas:
   contratado · executado · aceito · pago · saldo (planejado / sem planejamento) · meta de hoje × executado hoje.
   Aceite pendente é a etapa normal seguinte (executa → órgão aceita → paga), não um problema.
   Pagamentos recebidos: registre em `contratos/<C>/PAGAMENTOS.csv` (modelo em `fabrica/templates/`).
3. Os números vêm só de `medicoes/<OS>.json`, `contrato.yaml`, git, `TESTES.json` e `PLANEJAMENTO.csv`. Sem medição = 0, sem aceite = 0.
4. Para medir antes do relatório: `fabrica.py medir <C> <OS>` (exige auditoria aprovada). Nunca altere quantidades à mão.
5. Rode para todo contrato que tenha OS em `contratos/<C>/os/`. Faça commit e push dos relatórios.
