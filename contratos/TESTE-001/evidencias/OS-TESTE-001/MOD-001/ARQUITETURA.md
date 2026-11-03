# Arquitetura — MOD-001 Autenticação e controle de acesso

`app/security.py` (bcrypt, JWT com jti e versão de sessão, limitador), `app/deps.py` (usuário atual, `exigir(permissao)`), `app/routers/auth.py`, `app/routers/usuarios.py`, `frontend/src/auth.tsx`. Tabelas: usuarios, tokens_recuperacao, tokens_revogados.

Visão geral: `projetos/gestao-documental/docs/ARQUITETURA.md`.
