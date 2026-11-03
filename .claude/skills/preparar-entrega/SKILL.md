---
name: preparar-entrega
description: PREPARAR ENTREGA — roda checklist de 100 controles, auditoria e medição e monta o pacote ENTREGA_CONTRATO (20 pastas + ZIP + manifesto SHA-256).
---
# PREPARAR ENTREGA (G01, G17, G20)

1. `python3 fabrica/ferramentas/fabrica.py evidencias commits <C> <OS>` → `python3 fabrica/ferramentas/fabrica.py testes executar <C> <OS>` → `python3 fabrica/ferramentas/fabrica.py auditar <C> <OS>` → `python3 fabrica/ferramentas/fabrica.py medir <C> <OS>`.
2. `python3 fabrica/ferramentas/fabrica.py checklist <C> <OS>`: BLOQUEADA (crítico reprovado) → não entregar; corrigir. PENDENTE_VERIFICACAO_HUMANA → listar o que o humano precisa verificar (`contratos/<C>/checklist/resultados_humanos.yaml`).
3. `python3 fabrica/ferramentas/fabrica.py entrega <C> <OS>` → `contratos/<C>/entregas/<OS>/ENTREGA_<C>_<OS>.zip`.
4. Informe a situação real e as pendências. Aprovação técnica não é aceite do contratante.
