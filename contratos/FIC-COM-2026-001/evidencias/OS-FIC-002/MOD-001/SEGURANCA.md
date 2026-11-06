# Segurança e LGPD — MOD-001 MOD-001 Controle de sessão (TR M01, item 2 de 4)

## Dados pessoais tratados
Nome de usuário e IP das tentativas de login (tabela `login_attempts` e auditoria). Nenhuma senha é gravada.

## Controles implementados
Sessão revogável no servidor; limite de tentativas por usuário e por IP; trilha de auditoria de acesso; comparação de assinatura em tempo constante.

## Verificações executadas
9 testes do módulo + regressão (35 testes no total) executados pela fábrica; teste de navegador: token usado depois de **Sair** recebeu 401 e o bloqueio mostrou a mensagem na tela.

## Riscos residuais
Usuário inexistente responde mais rápido que senha errada (sem cálculo PBKDF2), o que permite descobrir nomes de usuário pelo tempo; não há política de retenção para `login_attempts`; token fica no `sessionStorage` (exposto a XSS se surgir falha de escape).
