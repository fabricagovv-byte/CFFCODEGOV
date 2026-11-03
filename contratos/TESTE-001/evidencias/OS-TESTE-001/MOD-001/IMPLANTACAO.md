# Implantação — MOD-001 Autenticação e controle de acesso

Migrações 0001 e 0002. Variáveis: JWT_SECRET (≥32 em homologação/produção), JWT_EXPIRA_MIN, LOGIN_MAX_TENTATIVAS, LOGIN_BLOQUEIO_MIN, BCRYPT_ROUNDS (padrão 12), URL_PUBLICA. Primeiro admin: `python -m app.seed` com ADMIN_EMAIL/ADMIN_SENHA.

Procedimento geral, atualização e rollback: `projetos/gestao-documental/docs/MANUAL_PUBLICACAO.md`.
