# Digitalgov Comunicação — MVP funcional

Aplicação FastAPI/SQLite com painel HTML/JS e regras operacionais implementadas:
- login com senha PBKDF2 e tokens HMAC (exige DG_COMM_SECRET)
- cadastro de usuários/perfis; canais; publicações com revisão por pessoa distinta; campanhas; contatos com consentimento; chamados; trilha de auditoria; exportação CSV de chamados; KPIs baseados no banco
- integração e-mail/SMS **não implementada**; o painel informa claramente o bloqueio
- não contém sistema federal homologado, integração de sistemas externos ou recursos exigidos em TR ainda não desenvolvidos

## Instalação

```bash
cd PLATAFORMA_COMUNICACAO
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export DG_COMM_SECRET=$(python -c 'import secrets;print(secrets.token_urlsafe(48))')
python -m app.cli init
python -m app.cli add-user --name 'Administrador' --username admin --role ADMIN --password 'SENHA-FORTE-DE-TESTE-1234'
python -m app.cli add-user --name 'Aprovador' --username revisor --role APPROVER --password 'OUTRA-SENHA-FORTE-1234'
uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Acesse http://127.0.0.1:8765. Em produção use HTTPS, IAM corporativo, sessão com cookies HttpOnly, CSRF, SGBD gerenciado, rotinas de backup, controles de privacidade, pentest e implantação supervisionada. Não use as senhas do exemplo em ambiente real.

## Banco e migrações (OS-FIC-002)

O banco é criado e atualizado por migrações versionadas em `migrations/NNNN_nome.up.sql`, cada uma com o `.down.sql` de reversão:

```bash
python -m app.cli init               # aplica as pendentes (banco antigo do pacote é reconhecido como versão 1)
python -m app.cli migrations         # mostra versão atual e pendentes
python -m app.cli rollback --to 1    # desfaz até a versão 1
```

## Sessão e acesso (OS-FIC-002)

- Cada login cria uma sessão no servidor; **Sair** revoga a sessão (`POST /api/logout`).
- Após 5 senhas erradas em 15 minutos o usuário é bloqueado por 15 minutos (20 por IP). Login certo, errado e bloqueado vão para a auditoria, sem a senha.
- Leitor (VIEWER) vê só publicações publicadas e não vê descrição nem contato dos chamados.
- Respostas com CSP, `X-Frame-Options: DENY`, `nosniff` e `Referrer-Policy`; a API não fica em cache.

## Testes
`pytest -q tests`

## Segurança e limitações
- Cada publicação precisa ser submetida, aprovada por usuário diferente e publicada; não há envio externo
- Auditoria em SQLite é adequada apenas a laboratório, não é imutável frente a administradores do banco
- Não possui upload de anexos, WebSocket de chat, envio real multicanal, retenção LGPD automatizada ou implantação homologada
- Separação do banco do módulo de fábrica; nenhuma métrica de projeto é convertida em horas humanas
