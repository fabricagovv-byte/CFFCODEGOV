# Arquitetura — MOD-004 MOD-004 Painel da fábrica — chave de acesso (ferramenta interna)

- Middleware HTTP confere a chave em tempo constante (`hmac.compare_digest`) para todo caminho `/api`; página inicial, arquivos estáticos e `/health` abrem sem chave.
- O painel envia `Authorization: Bearer <chave>` em todas as chamadas e volta à tela de acesso ao receber 401/503.
