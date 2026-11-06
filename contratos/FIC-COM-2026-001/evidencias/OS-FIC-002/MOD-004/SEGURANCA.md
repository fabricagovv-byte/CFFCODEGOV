# Segurança e LGPD — MOD-004 MOD-004 Painel da fábrica — chave de acesso (ferramenta interna)

## Dados pessoais tratados
Nomes dos profissionais (já existiam no painel).

## Controles implementados
Acesso fechado por padrão; chave fora do código; cabeçalhos de segurança.

## Verificações executadas
12 testes; navegador: chave errada mostrou "Chave de acesso inválida ou ausente" e a chave certa abriu o painel com 18 tarefas, sem erro de JavaScript.

## Riscos residuais
Chave única compartilhada, sem identificar a pessoa que aprovou ou acionou o START; sem limite de tentativas.
