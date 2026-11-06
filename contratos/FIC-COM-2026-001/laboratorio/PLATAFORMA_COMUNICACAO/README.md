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

## Testes
`pytest -q tests`

## Segurança e limitações
- Cada publicação precisa ser submetida, aprovada por usuário diferente e publicada; não há envio externo
- Auditoria em SQLite é adequada apenas a laboratório, não é imutável frente a administradores do banco
- Não possui upload de anexos, WebSocket de chat, envio real multicanal, retenção LGPD automatizada ou implantação homologada
- Separação do banco do módulo de fábrica; nenhuma métrica de projeto é convertida em horas humanas
