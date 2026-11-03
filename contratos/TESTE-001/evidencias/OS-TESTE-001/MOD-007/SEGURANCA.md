# Segurança e LGPD — MOD-007 Infraestrutura e documentação

## Dados pessoais e controles
Contêiner sem root; segredos só em .env (fora do git); CA corporativa opcional só no build (secret); TLS 1.2/1.3 + HSTS no proxy de borda; server_tokens off; limite de taxa em /api/auth/; backups com umask 077 e GPG opcional.

## Verificações executadas
- Testes automatizados do módulo (TESTES.json).
- Revisão independente G13/G10 em 2026-11-03 (ver REVISOES.md); achados corrigidos e cobertos por teste.

## Riscos residuais
Build depende de registro de imagens (Docker Hub limitou; usado espelho mirror.gcr.io nesta sessão).
