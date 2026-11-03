---
name: auditar-evidencias
description: AUDITAR EVIDÊNCIAS / AUDITAR MÓDULO — confere se as 15 evidências de cada módulo existem e correspondem a commits, testes e logs reais; bloqueia comprovações insuficientes.
---
# AUDITAR EVIDÊNCIAS (G17)

1. `python3 fabrica/ferramentas/fabrica.py evidencias commits <C> <OS>` (atualiza COMMITS.json/CODIGO_ALTERADO.md a partir do git).
2. `python3 fabrica/ferramentas/fabrica.py auditar <C> <OS>` → gera `evidencias/<OS>/AUDITORIA.md`.
3. Leia os achados. BLOQUEANTE = não pode medir como comprovado. PENDENCIA_HUMANA = falta registro de pessoa (responsável, revisão humana).
4. Confira por amostragem: abra 1 commit (`git show <sha> --stat`) e 1 log de teste por módulo e verifique que batem com o que os documentos dizem.
5. Registre inconsistências como bloqueio (`python3 fabrica/ferramentas/fabrica.py bloqueio --por G17 --texto "..."`).
