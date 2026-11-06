# Escopo — MOD-001 Controle de sessão (TR M01, item 2 de 4)

- Contrato: FIC-COM-2026-001 · OS: OS-FIC-002
- Item contratual: CAT-M01-SESSAO · Previsto: 202.5

## Descrição
Completa o item **controle de sessão** do módulo M01 do TR (escopo: RBAC por perfil, controle de sessão, MFA/SSO, segregação editorial). Corrige os achados 6 e 7 do diagnóstico.

## Funcionalidades
- Cada login cria uma sessão gravada no servidor (tabela `sessions`), com validade de 8 h.
- `POST /api/logout` revoga a sessão; o token deixa de valer na hora (HTTP 401).
- Bloqueio após 5 senhas erradas em 15 min por usuário (20 por IP), inclusive com a senha certa (HTTP 429).
- Login certo (`LOGIN_OK`), errado (`LOGIN_FALHOU`), bloqueado (`LOGIN_BLOQUEADO`) e saída (`LOGOUT`) na auditoria, sem a senha.
- Botão **Sair** da tela chama o servidor antes de limpar o navegador.

## Fora do escopo
- MFA e SSO (itens 3 de 4 do M01) — não feitos.
- Tela para o administrador listar e encerrar sessões de outros usuários.
- Desbloqueio manual pelo administrador.

Linha de base: o commit `f823f56` é a importação do código original do pacote DIGITALGOV (aparece no git porque os arquivos nasceram nele); não é trabalho desta OS e não é medido.
