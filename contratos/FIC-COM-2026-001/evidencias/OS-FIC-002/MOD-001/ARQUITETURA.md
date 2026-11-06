# Arquitetura — MOD-001 MOD-001 Controle de sessão (TR M01, item 2 de 4)

- **Tabelas novas** (migração 0002): `sessions(id, user_id, created_at, expires_at, revoked_at)` e `login_attempts(username, ip, success, at)` com índices por usuário e por IP.
- **Token**: assinado com HMAC-SHA256 (`DG_COMM_SECRET`) e agora carrega o identificador da sessão (`sid`); toda requisição confere a sessão no banco (existe, não revogada, não expirada) e o usuário ativo.
- **Endpoints**: `POST /api/login` (sessão + limite de tentativas), `POST /api/logout` (revoga), `GET /api/me` (não expõe o `sid`).
- **Decisão**: a contagem de falhas recomeça depois de um login certo; tentativas fora da janela de 15 min não contam.
