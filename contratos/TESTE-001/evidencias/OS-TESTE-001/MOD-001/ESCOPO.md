# Escopo — MOD-001 Autenticação e controle de acesso

- Contrato: TESTE-001 (fictício) · OS: OS-TESTE-001

## Descrição
Login com JWT, logout com revogação, sessão atual, recuperação e redefinição de senha, perfis (ADMIN, GESTOR, OPERADOR, CONSULTA), permissões e gestão de usuários.

## Funcionalidades
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me
- POST /api/auth/recuperar-senha
- POST /api/auth/redefinir-senha
- GET/POST/PATCH /api/usuarios
- Telas: Login, Esqueci a senha, Redefinir senha

## Fora do escopo
- Login gov.br
- MFA
- Envio real de e-mail (SMTP do órgão)
