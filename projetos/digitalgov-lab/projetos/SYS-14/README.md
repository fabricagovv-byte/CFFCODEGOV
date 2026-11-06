# SYS-14 — Registro de riscos

**Serviço de referência:** Segurança da Informação. Esta aplicação é um **CRUD local funcional de demonstração**, não o escopo definitivo do edital.

## Executar

```bash
cd projetos/SYS-14
python app.py --port 8014
```

Abra `http://127.0.0.1:8014`. O banco SQLite é criado em `data/records.sqlite3` de modo independente dos demais projetos.

## Testar

```bash
cd projetos/SYS-14
python -m unittest discover -s tests -v
```

Rotas: `GET /health`, `GET /api/records`, `GET /api/records/id`, `POST /api/records`, `PATCH /api/records/id`, `DELETE /api/records/id`.

**Segurança:** só para localhost. Não publicar sem SSO, autorização, TLS, controle de auditoria e políticas de LGPD. Sem UST contratuais atribuídas à existência deste código.

## Serviço especializado item 14

**Serviços de Gestão de Segurança da Informação** — Varredura estática de padrões de código de exemplo.

Abra `http://127.0.0.1:8014/service` após iniciar `app.py --port 8014`.
A tela executa uma operação especializada verificável, guarda os resultados em tabela `service_runs` do banco exclusivo e não gera UST automática.
