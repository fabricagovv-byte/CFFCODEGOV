# Escopo — MOD-004 Painel da fábrica — chave de acesso (ferramenta interna)

- Contrato: FIC-COM-2026-001 · OS: OS-FIC-002
- Item contratual: INTERNO-FABRICA · Previsto: 0

## Descrição
Painel da fábrica (ferramenta interna da contratada, não é entregável do contrato): corrige o achado 1 (tela vazia, já corrigido no diagnóstico) e o achado 2 (sem login). Não é medido.

## Funcionalidades
- Toda a API do painel exige a chave `DG_FACTORY_TOKEN` (32+ caracteres) no cabeçalho `Authorization`.
- Sem a variável configurada a API fica fechada (HTTP 503).
- Tela de acesso pede a chave, guarda só na aba do navegador e tem botão Sair.
- JavaScript e CSS em arquivos próprios, com CSP.
- `start_local.sh` recusa iniciar sem a chave.

## Fora do escopo
- Usuários e perfis individuais no painel (é uma chave única).
- HTTPS (continua só local).

Linha de base: o commit `f823f56` é a importação do código original do pacote DIGITALGOV (aparece no git porque os arquivos nasceram nele); não é trabalho desta OS e não é medido.
