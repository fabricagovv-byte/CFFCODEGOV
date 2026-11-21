#!/usr/bin/env bash
# Restaura o banco do projeto a partir de um backup, conferindo o SHA-256 antes.
# Uso: infra/scripts/restore.sh ARQUIVO.dump   (lê DATABASE_URL do .env; pare o sistema antes)
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
if [ -z "${DATABASE_URL:-}" ] && [ -f "$RAIZ/.env" ]; then set -a; . "$RAIZ/.env"; set +a; fi   # conexão já informada tem prioridade
ARQUIVO="${1:?informe o arquivo .dump}"
( cd "$(dirname "$ARQUIVO")" && sha256sum -c --status "$(basename "${ARQUIVO%.dump}").sha256" ) \
  || { echo "erro: o SHA-256 do backup não confere; nada foi restaurado" >&2; exit 1; }
pg_restore --clean --if-exists --no-owner --single-transaction --dbname "${DATABASE_URL/+psycopg/}" "$ARQUIVO"
echo "restaurado: $ARQUIVO"
