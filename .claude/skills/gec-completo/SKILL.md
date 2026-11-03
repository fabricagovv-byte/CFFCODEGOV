---
name: gec-completo
description: GEC — gera o Plano de Gestão da Execução Contratual completo em Word (identificação, escopo, serviços explicados, equipe exigida × designada, agentes e responsáveis, plano por projeto, cronograma diário e mensal, mensalidades, medição, custos, habilitação, SLAs, relatórios, riscos, estimativa × real e pendências).
---
# GEC completo

1. Garanta os insumos: `EDITAL.yaml` (skill analise-integral-edital), `contrato.yaml`, PERFIS/CATALOGO ou TABELA_UST, `PLANEJAMENTO.csv` (do usuário). Nomes da equipe podem vir no final.
2. `python3 fabrica/ferramentas/fabrica.py gec <ID>` → `contratos/<ID>/GEC.md` e `GEC.docx`.
3. Leia a seção 17 (pendências) e diga ao usuário o que falta para completar.
4. O GEC precisa de aprovação humana (responsável técnico e gestor do contrato) antes de valer.
