---
name: publicar-producao
description: PUBLICAR PRODUÇÃO — publica em produção SOMENTE com autorização humana explícita registrada. Invocável apenas pelo usuário.
disable-model-invocation: true
---
# PUBLICAR PRODUÇÃO

1. Verifique no `contrato.yaml`: `autorizacao_execucao.pode_publicar_producao: true`, com `autorizado_por`, `data` e `documento`. Se faltar, PARE.
2. Confirme com o usuário na conversa o ambiente, a versão (tag) e a janela.
3. Siga `docs/MANUAL_PUBLICACAO.md` seções 3–4 (backup antes!).
4. Verifique saúde; em falha, rollback (seção 5).
5. Registre: `python3 fabrica/ferramentas/fabrica.py decisao --por G11 --titulo "Publicação em produção <versão>" --texto "autorizado por ..., resultado ..."`.
