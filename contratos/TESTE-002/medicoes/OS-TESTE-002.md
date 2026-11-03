# Memória de cálculo — OS-TESTE-002

Gerado em 2026-11-03T01:05:04-03:00 pelo Medidor de UST (G15).

> **UST FICTÍCIAS — catálogo, perfis e valores de demonstração; sem valor para faturamento.**

| Módulo | Item | Unid. | Previsto | Comprovado | Aceito | Responsável |
|---|---|---|---|---|---|---|
| MOD-100 Base modular para cadastros | SRV-BASE | UST | 12.2 | 12.2 | 0 | A CADASTRAR |
| MOD-101 Cadastro de interessados | SRV-CRUD-M | UST | 24.4 | 24.4 | 0 | A CADASTRAR |
| MOD-102 Cadastro de protocolos | SRV-CRUD-A | UST | 43.8 | 43.8 | 0 | A CADASTRAR |
| **Total** | | | **80.4** | **80.4** | **0** | |

## Horas por perfil (catálogo do contrato)

| Perfil | Horas | Valor/hora | Valor previsto |
|---|---|---|---|
| DESENVOLVEDOR_SENIOR | 32 | R$ 130,00 | R$ 4.160,00 |
| ANALISTA_TESTES | 12 | R$ 85,00 | R$ 1.020,00 |
| ANALISTA_REQUISITOS | 10 | R$ 110,00 | R$ 1.100,00 |
| DESENVOLVEDOR_PLENO | 16 | R$ 95,00 | R$ 1.520,00 |
| **Total** | **70** | | **R$ 7.800,00** |

## Memória por item

- **MOD-100**: previsto=12.2 UST (OS OS-TESTE-002, item SRV-BASE) [fórmula HORAS_X_FATOR: 10 h = DESENVOLVEDOR_SENIOR 8 h, ANALISTA_TESTES 2 h; valor R$ 1.210,00]; comprovado=12.2 pois auditoria técnica=APROVADO; aceito=0 (sem aceite registrado)
- **MOD-101**: previsto=24.4 UST (OS OS-TESTE-002, item SRV-CRUD-M) [fórmula HORAS_X_FATOR: 24 h = ANALISTA_REQUISITOS 4 h, DESENVOLVEDOR_PLENO 16 h, ANALISTA_TESTES 4 h; valor R$ 2.300,00]; comprovado=24.4 pois auditoria técnica=APROVADO; aceito=0 (sem aceite registrado)
- **MOD-102**: previsto=43.8 UST (OS OS-TESTE-002, item SRV-CRUD-A) [fórmula HORAS_X_FATOR: 36 h = ANALISTA_REQUISITOS 6 h, DESENVOLVEDOR_SENIOR 24 h, ANALISTA_TESTES 6 h; valor R$ 4.290,00]; comprovado=43.8 pois auditoria técnica=APROVADO; aceito=0 (sem aceite registrado)

## Regras aplicadas

- Previsto: quantidade da OS para o item da tabela contratual.
- Comprovado: igual ao previsto somente se a auditoria técnica do módulo for APROVADO (evidências completas, commits reais, testes reais sem falhas); caso contrário 0. Ajuste esta regra se o contrato prever medição parcial.
- Aceito: somente com ACEITE.md em status ACEITO, com `aceito_por` e `documento` (termo do contratante). Nunca maior que o comprovado.
- Conversão entre horas e UST somente pela fórmula declarada no contrato (medicao.formula) e pelos fatores de PERFIS.csv; sem fórmula, não há conversão.
