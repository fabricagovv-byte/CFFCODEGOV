---
name: verificar-codigo
description: VERIFICAR CÓDIGO / REVISAR CÓDIGO / EXECUTAR TESTES — executa testes reais, typecheck, build e revisões de código e segurança; registra resultados nas evidências.
---
# VERIFICAR CÓDIGO (G12, G13, G10)

1. `python3 fabrica/ferramentas/fabrica.py testes executar <CONTRATO> <OS>` (roda os comandos do YAML da OS e grava JUnit + log por módulo).
2. Frontend: `npm run typecheck && npm run build` na pasta do frontend; registre a saída em LOGS_TESTES do MOD de infraestrutura se relevante.
3. Revisão (G13): leia o diff (`git diff`/`git log -p`), registre achados com severidade em REVISOES.md do módulo, seção "Revisão automatizada".
4. Segurança (G10): OWASP Top 10, segredos, dependências, LGPD → SEGURANCA.md do módulo.
5. Falhas viram tarefas: `python3 fabrica/ferramentas/fabrica.py tarefas criar --agente <dev> --descricao "Defeito: ..." --prioridade ALTA`.
6. Informe números reais (testes, falhas) — copiados da saída.
