---
name: analise-integral-edital
description: ANÁLISE INTEGRAL DO EDITAL — com os 24 agentes da Fábrica Governamental, lê todos os documentos e anexos e entrega - explicação técnica de cada serviço, profissionais exigidos, habilitação, SLAs e glosas, regras de medição (UST/PF/horas), mensalidades e custos estimados, relatórios e evidências exigidos, cronograma e GEC, sempre com cláusula e página e separando estimativa de execução real.
---
# Análise integral do edital (G01–G24)

1. **Ler tudo** (G02): edital, TR, minuta de contrato, anexos, planilhas. PDF: skill de PDF disponível. Anote documento + página de cada trecho usado. Nada fora dos documentos — o que não estiver lá vira "não consta — perguntar".
2. **Preencher `contratos/<ID>/EDITAL.yaml`** (modelo comentado em `fabrica/templates/EDITAL.yaml`):
   - `servicos` com **explicação técnica** de cada item (G02/G05);
   - `equipe_exigida` (perfis, quantidade, formação, anos, certificações) (G18);
   - `habilitacao` (jurídica, fiscal/trabalhista, técnica, econômico-financeira) (G21);
   - `slas` (indicador, meta, medição, glosa) (G23);
   - `medicao` + `pagamento`, `documentos_exigidos`, `relatorios_exigidos`, `prazos`, `tecnologias_exigidas`;
   - cada item com `origem` (documento, cláusula, página).
3. **Medição:** copie a tabela UST ou os perfis (valor/hora, fator) e o catálogo de horas para `TABELA_UST.csv` / `PERFIS.csv` / `CATALOGO_SERVICOS.csv`; fórmula em `contrato.yaml medicao.formula` (G15, G16, G22).
4. **Confronto:** `python3 fabrica/ferramentas/fabrica.py edital confrontar <ID>` (o que a empresa atende / ajustar / falta).
5. **Plano e cronograma** (G04, G24): com o PLANEJAMENTO do usuário → `python3 fabrica/ferramentas/fabrica.py planejamento consolidar <ID>`; capacidade: `python3 fabrica/ferramentas/fabrica.py capacidade <ID>`.
6. **GEC completo:** `python3 fabrica/ferramentas/fabrica.py gec <ID>` → GEC.md + GEC.docx (17 seções, ESTIMATIVA × REAL, pendências).
7. Responda ao usuário: resumo do objeto, serviços, equipe exigida, riscos (habilitação, SLA, prazos), o que falta ele enviar. Conflitos entre documentos → análise humana/jurídica.
