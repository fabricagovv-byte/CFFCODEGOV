# Padrões de medição técnica — referências oficiais

Estes são referenciais para **desempenho de engenharia**, não para criar UST do edital.

- **DORA / Google, pesquisa oficial sobre desempenho em entrega de software:** https://dora.dev/research/2024/dora-report/2024-dora-accelerate-state-of-devops-report.pdf — tempo de mudança, frequência de implantação, recuperação após falha, taxa de falha e retrabalho de implantação.
- **DORA (guia histórico de métricas de 2026):** https://dora.dev/insights/dora-metrics-history/ — definições e cautela de interpretação.
- **GitLab, Value Stream Analytics:** https://docs.gitlab.com/user/group/value_stream_analytics/ — registro de estágios e durações para detectar gargalos.
- **Microsoft, Azure DevOps / lead time e cycle time:** https://learn.microsoft.com/en-us/azure/devops/report/dashboards/cycle-time-and-lead-time?view=azure-devops — duração entre criação, início e conclusão.

## Aplicação no relatório

1. Prazo planejado versus prazo executado; início/fim a partir do SQLite, nunca inventados.
2. Quantidade de demandas abertas, concluídas, tecnicamente verificadas e aceitas.
3. Taxa de testes e falhas a partir de pipelines executados; resultado ausente = N/A.
4. Horas humanas calculadas somente sobre registros humanos reais.
5. UST: **catálogo pactuado + OS autorizada + evidência + fator acordado + aceite**, não métrica DORA.

**Origem:** páginas públicas oficiais; conteúdo sintetizado, sem reprodução de relatórios proprietários.
