# SYS-13 — Registro de políticas

**Serviço de referência:** Governança de TI. Esta aplicação é um **CRUD local funcional de demonstração**, não o escopo definitivo do edital.

## Executar

```bash
cd projetos/SYS-13
python app.py --port 8013
```

Abra `http://127.0.0.1:8013`. O banco SQLite é criado em `data/records.sqlite3` de modo independente dos demais projetos.

## Testar

```bash
cd projetos/SYS-13
python -m unittest discover -s tests -v
```

Rotas: `GET /health`, `GET /api/records`, `GET /api/records/id`, `POST /api/records`, `PATCH /api/records/id`, `DELETE /api/records/id`.

**Segurança:** só para localhost. Não publicar sem SSO, autorização, TLS, controle de auditoria e políticas de LGPD. Sem UST contratuais atribuídas à existência deste código.

## Serviço especializado item 13

**Serviços de Governança de TI** — Matriz de riscos e controle de prioridade.

Abra `http://127.0.0.1:8013/service` após iniciar `app.py --port 8013`.
A tela executa uma operação especializada verificável, guarda os resultados em tabela `service_runs` do banco exclusivo e não gera UST automática.
