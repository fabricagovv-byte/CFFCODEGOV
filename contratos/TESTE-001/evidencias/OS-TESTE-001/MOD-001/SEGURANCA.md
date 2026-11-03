# Segurança e LGPD — MOD-001 Autenticação e controle de acesso

## Dados pessoais e controles
Dados pessoais: nome e e-mail. Controles: bcrypt; política de senha; bloqueio após 5 falhas; mensagem idêntica para e-mail inexistente; token de recuperação só como hash, 30 min, uso único e atômico; troca de senha encerra sessões (versao_sessao); logout revoga jti; usuário desativado perde acesso imediato.

## Verificações executadas
- Testes automatizados do módulo (TESTES.json).
- Revisão independente G13/G10 em 2026-11-03 (ver REVISOES.md); achados corrigidos e cobertos por teste.

## Riscos residuais
Limitador em memória por worker; sem MFA; SMTP não integrado.
