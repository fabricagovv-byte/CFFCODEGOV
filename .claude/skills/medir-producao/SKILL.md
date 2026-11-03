---
name: medir-producao
description: MEDIR PRODUÇÃO — calcula UST/PF conforme a tabela contratual, com memória de cálculo e separação previsto/comprovado/aceito; também calcula médias históricas por profissional a partir de dados enviados pelo usuário.
---
# MEDIR PRODUÇÃO (G15 Medidor de UST, G16 Pontos de Função)

1. Garanta auditoria atualizada (skill auditar-evidencias).
2. `python3 fabrica/ferramentas/fabrica.py medir <C> <OS>` → `contratos/<C>/medicoes/<OS>.md` e MEDICAO.md por módulo.
3. Regras: previsto = OS; comprovado = só com auditoria técnica APROVADO; aceito = só com ACEITE.md assinado pelo contratante (status ACEITO + aceito_por + documento).
4. Pontos de função: contagem manual pela metodologia do contrato (IFPUG/NESMA/SISP), com memória (fronteira, ALI/AIE, EE/SE/CE, complexidade) — revisão por profissional certificado quando o contrato exigir.
5. Médias por profissional (ex.: "UST média em trabalho difícil"): o usuário envia `PRODUCAO_HISTORICA.csv` (modelo em fabrica/templates). Rode `python3 fabrica/ferramentas/fabrica.py producao estatisticas <arquivo>`. As médias valem só para planejamento interno, não para faturar.
6. Para aumentar a produção de forma legítima: `python3 fabrica/ferramentas/fabrica.py oportunidades <C> <OS>` lista trabalho comprovado que pode corresponder a itens do catálogo ainda não medidos. Cada item depende de enquadramento no contrato e confirmação humana; nunca some sem trabalho real nem conte duas vezes.
7. Nunca converta UST ↔ PF ↔ horas sem fórmula escrita no contrato. Linhas de código não comprovam quantidade faturável.
