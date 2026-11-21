#!/usr/bin/env bash
# Restaura o banco central (e os documentos, se houver) a partir de um backup, conferindo o SHA-256.
# Uso: infra/scripts/restore.sh PASTA_DO_BACKUP CARIMBO      (pare o gerenciador antes)
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
if [ -z "${GERENCIADOR_DATABASE_URL:-}" ] && [ -f "$RAIZ/.env" ]; then set -a; . "$RAIZ/.env"; set +a; fi   # conexão já informada tem prioridade
PASTA="${1:?informe a pasta do backup}"; CARIMBO="${2:?informe o carimbo, ex.: 20261106T180000}"
URL="${GERENCIADOR_DATABASE_URL:?defina GERENCIADOR_DATABASE_URL}"
ARQUIVOS="${GERENCIADOR_ARQUIVOS:-$RAIZ/dados/arquivos}"
( cd "$PASTA" && sha256sum -c --status "backup-$CARIMBO.sha256" ) || { echo "erro: SHA-256 não confere; nada foi restaurado" >&2; exit 1; }
pg_restore --clean --if-exists --no-owner --single-transaction --dbname "${URL/+psycopg/}" "$PASTA/gerenciador-$CARIMBO.dump"
if [ -f "$PASTA/documentos-$CARIMBO.tar.gz" ]; then
  mkdir -p "$ARQUIVOS" && tar -C "$ARQUIVOS" -xzf "$PASTA/documentos-$CARIMBO.tar.gz"
fi
echo "restaurado: carimbo $CARIMBO"
