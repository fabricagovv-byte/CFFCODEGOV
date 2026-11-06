# Plataforma de Comunicação Institucional

Dois sistemas:

| Pasta | Sistema | Porta |
|---|---|---|
| `PLATAFORMA_COMUNICACAO/` | Plataforma de comunicação (API + telas) | 8765 |
| `FABRICA/` | Painel de controle interno da contratada | 8777 (só no próprio servidor) |

Camadas da plataforma: banco de dados em `migrations/` e `app/db.py`; back-end em `app/` (rotas em `app/rotas/`); front-end em `static/`.

## Executar no computador (sem Docker)

Requisitos: Python 3.11 ou mais novo.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r PLATAFORMA_COMUNICACAO/requirements-dev.txt -r FABRICA/requirements-dev.txt
cp .env.example .env            # preencha DG_COMM_SECRET e DG_FACTORY_TOKEN
set -a && . ./.env && set +a
(cd PLATAFORMA_COMUNICACAO && python -m app.cli init && python -m app.cli add-user --name Administrador --username admin --role ADMIN --password 'TROQUE-ESTA-SENHA')
./start_local.sh
```

Plataforma: http://127.0.0.1:8765 · Painel: http://127.0.0.1:8777 (chave = DG_FACTORY_TOKEN)

## Executar com Docker

```bash
cp .env.example .env            # preencha
docker compose up -d --build
docker compose exec comunicacao python -m app.cli add-user --name Administrador --username admin --role ADMIN --password 'TROQUE-ESTA-SENHA'
```

Plataforma: http://127.0.0.1:8080 (porta em `PORTA_HTTP`). Publicação com TLS: `docs/MANUAL_PUBLICACAO.md`.

## Testes

```bash
(cd PLATAFORMA_COMUNICACAO && python -m pytest -q tests)
(cd FABRICA && python -m pytest -q tests)
```

## Documentos

- `docs/MANUAL_PUBLICACAO.md` — publicação em homologação e produção, e como voltar à versão anterior
- `docs/MANUAL_OPERACAO.md` — rotina, backup, usuários, monitoramento
- `docs/PLANO_CONTINUIDADE.md` — recuperação de desastres
