---
name: fluxo-os
description: FLUXO DA OS / EXECUTAR TUDO — roda a OS do começo ao fim como um grafo de etapas com pontos de retomada (autorização, testes, commits, auditoria, medição, relatórios, checklist, entrega); para em falha e pausa para aprovação humana.
---
# Fluxo da OS (execução durável)

Conceitos do LangGraph aplicados (`fabrica/conhecimento/langgraph/CONCEITOS.md`).

1. `python3 fabrica/ferramentas/fabrica.py fluxo <ID> <OS>` — retoma do primeiro nó não concluído (`--do-zero` reinicia; `--ate medicao` para antes).
2. **PARADO** (falha): leia o erro, use depuracao-sistematica, corrija, rode de novo (retoma do ponto).
3. **PAUSADO** (humano): autorização da OS ausente, ou controles críticos aguardando verificação. Peça ao usuário; após a verificação real: `python3 fabrica/ferramentas/fabrica.py fluxo <ID> <OS> --aprovado-por "Nome (cargo)"`.
4. O estado fica em `contratos/<ID>/fluxos/<OS>.json` (sobrevive a sessões).
