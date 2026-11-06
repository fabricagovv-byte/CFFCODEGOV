# Segurança e LGPD — MOD-002 MOD-002 Correções de validação e privacidade (M03, M05, M07, M08)

## Dados pessoais tratados
Nome e e-mail de contatos; descrição de chamados (pode conter dado pessoal).

## Controles implementados
Minimização para o perfil leitor; validação de entrada; proteção contra injeção em planilhas; integridade referencial.

## Verificações executadas
8 testes do módulo + regressão (34 testes); navegador: leitor viu só a publicação publicada; e-mail inválido recusado com mensagem "E-mail inválido".

## Riscos residuais
O leitor ainda vê formulários e botões de ação na tela (o servidor recusa); validação de e-mail é de formato, não confirma que o endereço existe.
