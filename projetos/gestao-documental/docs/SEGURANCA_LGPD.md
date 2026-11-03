# Segurança e LGPD

## Inventário de dados pessoais

| Dado | Onde | Finalidade | Observação |
|---|---|---|---|
| Nome e e-mail de usuários | `usuarios` | autenticação e responsabilização | mínimo necessário |
| IP e ações | `auditoria` | segurança e rastreabilidade (Marco Civil, art. 15, quando aplicável) | retenção a definir pelo órgão |
| Campo "interessado" | `documentos` | identificação do interessado no documento | pode conter dado pessoal: classificar como RESTRITO quando houver |
| Conteúdo dos PDFs | volume de arquivos | gestão documental | pode conter dados pessoais/sensíveis |

A base legal e a finalidade do tratamento são definidas pelo **controlador (órgão)**; a contratada atua como operadora.

## Controles implementados (verificados por testes automatizados)

- Senhas com bcrypt; política mínima (10 caracteres, letras e números).
- JWT com expiração e revogação (logout); segredo obrigatório e forte em homologação/produção.
- Bloqueio após 5 falhas de login por 15 minutos; mesma mensagem para e-mail inexistente e senha errada.
- Recuperação de senha sem revelar se o e-mail existe; token aleatório guardado só como hash, 30 min, uso único.
- Autorização por perfil em todas as rotas; documentos não visíveis retornam 404.
- Upload: extensão, assinatura `%PDF-`, tamanho máximo, nome sanitizado, armazenamento com nome aleatório, SHA-256.
- Trilha de auditoria de login, falhas, consultas a documentos restritos, criação, alteração, arquivamento, upload e download; imutável no PostgreSQL.
- Cabeçalhos: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy`, `Cache-Control: no-store`; HSTS no proxy TLS.
- Contêiner do backend roda como usuário sem privilégios.
- Nenhum segredo no repositório (`.env` ignorado; checklist C044 varre o projeto).

## Revisão independente (G13/G10) — 2026-11-03

Corrigidos e cobertos por teste: IP forjável via X-Forwarded-For; troca de senha não encerrava sessões; OPERADOR desarquivava e reclassificava documentos; e-mail > 60 caracteres gerava erro 500 e perdia a auditoria no PostgreSQL; PATCH com `null`; corrida no uso do token de redefinição; X-Request-ID sem validação; `/api/docs` exposto em produção; cabeçalhos anulados em `/assets/`; `server_tokens`; arquivos órfãos; backup com permissão aberta (agora `umask 077` + GPG opcional); limite de taxa em `/api/auth/` no Nginx e na recuperação de senha.

## Pendências / riscos residuais

- Limitador de login em memória por worker (com `WORKERS=4` são até 4× as tentativas); para produção com réplicas, mover para Redis.
- O e-mail digitado nas falhas de login fica na trilha de auditoria (necessário para investigação; tratar como dado pessoal na política de retenção).

- Antivírus nos PDFs enviados (ex.: ClamAV) — depende de decisão do órgão.
- Limitador de login em memória: com várias réplicas, usar Redis.
- MFA / login gov.br não implementados nesta OS de teste.
- Criptografia do volume de arquivos e do banco em repouso depende da infraestrutura do órgão.
- Pentest independente não realizado.

## Resposta a incidentes

1. Conter (desativar usuário, trocar segredos). 2. Preservar evidências (logs, auditoria). 3. Avaliar risco aos titulares. 4. Comunicar o encarregado do órgão; a comunicação à ANPD e aos titulares é decisão do controlador. 5. Registrar lições aprendidas.
