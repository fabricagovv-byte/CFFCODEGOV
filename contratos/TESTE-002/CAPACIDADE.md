# Capacidade e estimativa de produção — TESTE-002

Gerado em 2026-11-03T06:47:01-03:00 pelo Planejador de Cronograma e Capacidade (G24).

> **ESTIMATIVA.** Não é medição nem promessa ao órgão. A produção real sai do trabalho comprovado e do aceite. Premissas: 8 h/dia × aproveitamento 0.8 = 6.4 h produtivas por pessoa; UST pelo fator de cada perfil (fórmula HORAS_X_FATOR); PF por produtividade não informada.

| Pessoa | Cargo | Perfil do catálogo | Horas produtivas/dia | UST/dia | PF/dia | Valor/dia |
|---|---|---|---|---|---|---|
| DESENVOLVEDOR_SENIOR #1 (simulado) | DESENVOLVEDOR_SENIOR | DESENVOLVEDOR_SENIOR | 6,4 | 8,32 | — | R$ 832,00 |
| DESENVOLVEDOR_PLENO #1 (simulado) | DESENVOLVEDOR_PLENO | DESENVOLVEDOR_PLENO | 6,4 | 6,40 | — | R$ 608,00 |
| DESENVOLVEDOR_PLENO #2 (simulado) | DESENVOLVEDOR_PLENO | DESENVOLVEDOR_PLENO | 6,4 | 6,40 | — | R$ 608,00 |
| ANALISTA_REQUISITOS #1 (simulado) | ANALISTA_REQUISITOS | ANALISTA_REQUISITOS | 6,4 | 7,68 | — | R$ 704,00 |
| ANALISTA_TESTES #1 (simulado) | ANALISTA_TESTES | ANALISTA_TESTES | 6,4 | 5,76 | — | R$ 544,00 |

## Equipe inteira

| Período | Horas | UST | PF | Valor |
|---|---|---|---|---|
| Por dia | 32,0 | 34,56 | — | R$ 3.296,00 |
| Por mês (21 dias úteis) | 672 | 725,76 | — | R$ 69.216,00 |

## Como melhorar a estimativa

- Informe a produtividade (h/PF) do contrato ou do seu histórico em `CONFIGURACAO_FABRICA.yaml` (producao.produtividade_horas_por_pf).
- Cadastre cargos que correspondam aos perfis do catálogo (PERFIS.csv).
- Preencha PRODUCAO_HISTORICA.csv com o que já foi aceito: a comparação mostra o quanto a estimativa está otimista.
