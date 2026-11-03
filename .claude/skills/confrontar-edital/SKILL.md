---
name: confrontar-edital
description: CONFRONTAR EDITAL — cruza as exigências do edital (equipe, certificações, tecnologias, relatórios, documentos, medição) com o documento base da empresa e diz ao usuário o que já atende, o que ajustar e o que falta; adapta títulos, seções e periodicidade ao que o edital pede.
---
# CONFRONTAR EDITAL (G02 Analista de Editais, G18 Gestor de Profissionais, G04)

1. Leia edital/TR/contrato (skill analisar-edital) e preencha `contratos/<ID>/EDITAL.yaml`: equipe_exigida (perfil, quantidade, palavras_chave, certificações, anos, formação, origem), tecnologias, certificações da empresa, relatórios exigidos, documentos exigidos com o nome que o edital usa, unidade de medição, prazos. **Cite a origem de cada item.**
2. Se o edital usa outro nome ou estrutura (ex.: "Plano de Trabalho" em vez de PPJ, "RME" em vez de relatório mensal, seções obrigatórias), ajuste `documentos.*.titulo` e `secoes_extras` — os geradores passam a usar isso automaticamente.
3. Garanta que o documento base foi importado (`python3 fabrica/ferramentas/fabrica.py planilha importar <ID> DOCUMENTO_BASE.xlsx`).
4. `python3 fabrica/ferramentas/fabrica.py edital confrontar <ID>` → `contratos/<ID>/CONFRONTO_EDITAL.md`.
5. Responda ao usuário em 3 listas curtas: ✔ já atende · ⚠ ajustar · ✘ falta (o que ele precisa mandar). Lembre que a comparação é por palavras-chave e que comprovantes de equipe/certificação exigem conferência humana.
