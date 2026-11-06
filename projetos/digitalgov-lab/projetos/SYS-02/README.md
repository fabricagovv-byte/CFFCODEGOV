# SYS-02 — Cadastro de módulos

**Serviço de referência:** Desenvolvimento de Sistemas. Esta aplicação é um **CRUD local funcional de demonstração**, não o escopo definitivo do edital.

## Executar

```bash
cd projetos/SYS-02
python app.py --port 8002
```

Abra `http://127.0.0.1:8002`. O banco SQLite é criado em `data/records.sqlite3` de modo independente dos demais projetos.

## Testar

```bash
cd projetos/SYS-02
python -m unittest discover -s tests -v
```

Rotas: `GET /health`, `GET /api/records`, `GET /api/records/id`, `POST /api/records`, `PATCH /api/records/id`, `DELETE /api/records/id`.

**Segurança:** só para localhost. Não publicar sem SSO, autorização, TLS, controle de auditoria e políticas de LGPD. Sem UST contratuais atribuídas à existência deste código.

## Serviço especializado item 02

**Suporte técnico de 2º nível** — Planejamento de visita técnica, janela e atendimento.

Abra `http://127.0.0.1:8002/service` após iniciar `app.py --port 8002`.
A tela executa uma operação especializada verificável, guarda os resultados em tabela `service_runs` do banco exclusivo e não gera UST automática.
