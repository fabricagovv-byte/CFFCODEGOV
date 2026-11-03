---
name: depuracao-sistematica
description: Use ao encontrar qualquer erro, teste falhando ou comportamento inesperado, ANTES de propor correção - encontre a causa raiz em 4 fases (investigar, comparar com o que funciona, hipótese testada, corrigir com teste).
---
# Depuração sistemática

Adaptado de superpowers/systematic-debugging (MIT) — original em `fabrica/conhecimento/superpowers/systematic-debugging/SKILL.md`.

**Lei:** nenhuma correção sem causa raiz identificada.

1. **Investigar:** leia a mensagem de erro inteira; reproduza com um comando; veja o que mudou (`git log -p`, `git diff`); colete evidência em cada fronteira (entrada/saída).
2. **Comparar:** ache um caso parecido que funciona; liste as diferenças.
3. **Hipótese:** uma de cada vez, a menor mudança que a testa. Errou? nova hipótese — não empilhe correções.
4. **Corrigir:** teste que reproduz o problema (skill tdd) → correção → verificar-antes-de-concluir.

Três correções falharam? Pare e questione a arquitetura com o usuário/Tech Lead (E02). Registre a causa em `python3 fabrica/ferramentas/fabrica.py decisao` quando afetar o projeto.
Exemplos reais desta fábrica: PostgreSQL desligado (fluxo parou em testes), `*[...] or [...]` (erro de sintaxe), YAML com `:` sem aspas.
