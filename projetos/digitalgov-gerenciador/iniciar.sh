#!/usr/bin/env bash
# Inicia o gerenciador no Linux/macOS: carrega o .env, aplica as migrações e sobe o painel na porta 8200.
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] || { echo "Crie o arquivo .env a partir do .env.example (veja docs/MANUAL_INSTALACAO.md)"; exit 1; }
set -a; . ./.env; set +a
[ -d .venv ] && . .venv/bin/activate
cd backend
alembic upgrade head
exec uvicorn app.main:app --host "${HOST:-127.0.0.1}" --port "${PORTA:-8200}"
