---
name: tdd
description: Use ao implementar qualquer funcionalidade ou correção, antes de escrever o código de produção - escreva o teste que falha, veja falhar, escreva o mínimo para passar, refatore (vermelho-verde-refatorar).
---
# Desenvolvimento guiado por testes (TDD)

Adaptado de superpowers/test-driven-development (MIT) — original em `fabrica/conhecimento/superpowers/test-driven-development/SKILL.md`.

**Regra:** nenhum código de produção sem um teste que falhou antes.

1. **Vermelho:** escreva um teste pequeno para o comportamento exigido (ligue ao requisito do edital: `# REQ-012`). Rode e **veja falhar pelo motivo certo**.
2. **Verde:** escreva o mínimo de código para passar. Rode.
3. **Refatorar:** limpe mantendo verde. Rode de novo.
4. Repita por comportamento. Bug encontrado = primeiro um teste que reproduz o bug.

Na fábrica: testes por módulo (`test_modNNN_*.py`, `*.test.tsx`), cadastros via `crud gerar` já trazem a suíte base — regras específicas do edital entram por TDD em cima dela. Sem teste executado, não há entrega (regra 20).
