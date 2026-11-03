# Segurança e LGPD — MOD-004 Pesquisa

## Dados pessoais e controles
Resultados respeitam o perfil (CONSULTA não vê RESTRITO/SIGILOSO).

## Verificações executadas
- Testes automatizados do módulo (TESTES.json).
- Revisão independente G13/G10 em 2026-11-03 (ver REVISOES.md); achados corrigidos e cobertos por teste.

## Riscos residuais
LIKE com curinga inicial não usa índice; para grande volume, usar full-text search do PostgreSQL.
