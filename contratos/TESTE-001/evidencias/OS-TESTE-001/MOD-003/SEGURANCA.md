# Segurança e LGPD — MOD-003 Upload de PDF

## Dados pessoais e controles
PDF pode conter dados pessoais; download respeita classificação do documento e é auditado. Path traversal bloqueado (nome aleatório + verificação de caminho).

## Verificações executadas
- Testes automatizados do módulo (TESTES.json).
- Revisão independente G13/G10 em 2026-11-03 (ver REVISOES.md); achados corrigidos e cobertos por teste.

## Riscos residuais
Sem antivírus; criptografia em repouso depende da infraestrutura.
