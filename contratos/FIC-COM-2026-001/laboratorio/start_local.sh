#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export DG_COMM_SECRET="${DG_COMM_SECRET:-}"
if [[ ${#DG_COMM_SECRET} -lt 32 ]]; then
  echo 'ERRO: defina DG_COMM_SECRET com 32+ caracteres. Use: export DG_COMM_SECRET=$(python -c "import secrets;print(secrets.token_urlsafe(48))")' >&2
  exit 1
fi
export DG_FACTORY_TOKEN="${DG_FACTORY_TOKEN:-}"
if [[ ${#DG_FACTORY_TOKEN} -lt 32 ]]; then
  echo 'ERRO: defina DG_FACTORY_TOKEN (chave do painel da fábrica, 32+ caracteres). Use: export DG_FACTORY_TOKEN=$(python -c "import secrets;print(secrets.token_urlsafe(48))")' >&2
  exit 1
fi
(cd "$ROOT/FABRICA" && python -m app.cli init && python -m app.cli seed-fiction)
(cd "$ROOT/PLATAFORMA_COMUNICACAO" && python -m app.cli init)
echo 'Painel da fábrica: http://127.0.0.1:8777 (entre com a chave DG_FACTORY_TOKEN)'
echo 'Comunicação: http://127.0.0.1:8765'
echo 'Crie usuários no módulo de comunicação antes de acessar.'
(cd "$ROOT/FABRICA" && uvicorn app.main:app --host 127.0.0.1 --port 8777) & PID1=$!
(cd "$ROOT/PLATAFORMA_COMUNICACAO" && uvicorn app.main:app --host 127.0.0.1 --port 8765) & PID2=$!
trap 'kill $PID1 $PID2 2>/dev/null || true' EXIT
wait
