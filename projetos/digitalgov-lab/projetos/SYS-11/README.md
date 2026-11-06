# SYS-11 — Registro de marcos

**Serviço de referência:** Gerenciamento de Projetos. Esta aplicação é um **CRUD local funcional de demonstração**, não o escopo definitivo do edital.

## Executar

```bash
cd projetos/SYS-11
python app.py --port 8011
```

Abra `http://127.0.0.1:8011`. O banco SQLite é criado em `data/records.sqlite3` de modo independente dos demais projetos.

## Testar

```bash
cd projetos/SYS-11
python -m unittest discover -s tests -v
```

Rotas: `GET /health`, `GET /api/records`, `GET /api/records/id`, `POST /api/records`, `PATCH /api/records/id`, `DELETE /api/records/id`.

**Segurança:** só para localhost. Não publicar sem SSO, autorização, TLS, controle de auditoria e políticas de LGPD. Sem UST contratuais atribuídas à existência deste código.

## Serviço especializado item 11

**Gerenciamento de projetos** — Cálculo de caminho crítico em projeto com dependências.

Abra `http://127.0.0.1:8011/service` após iniciar `app.py --port 8011`.
A tela executa uma operação especializada verificável, guarda os resultados em tabela `service_runs` do banco exclusivo e não gera UST automática.
