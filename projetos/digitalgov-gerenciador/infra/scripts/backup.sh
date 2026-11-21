#!/usr/bin/env bash
# Backup do banco central do gerenciador (pg_dump) e dos documentos enviados, com SHA-256 e retenção.
# Uso: infra/scripts/backup.sh [DESTINO]      (lê GERENCIADOR_DATABASE_URL e GERENCIADOR_ARQUIVOS do .env)
set -euo pipefail
umask 077   # contém dados pessoais e documentos dos contratos
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
if [ -z "${GERENCIADOR_DATABASE_URL:-}" ] && [ -f "$RAIZ/.env" ]; then set -a; . "$RAIZ/.env"; set +a; fi   # conexão já informada tem prioridade
DESTINO="${1:-$RAIZ/backups}"
URL="${GERENCIADOR_DATABASE_URL:?defina GERENCIADOR_DATABASE_URL}"
ARQUIVOS="${GERENCIADOR_ARQUIVOS:-$RAIZ/dados/arquivos}"
CARIMBO="$(date +%Y%m%dT%H%M%S)"
mkdir -p "$DESTINO"
pg_dump --format=custom --no-owner --file "$DESTINO/gerenciador-$CARIMBO.dump" "${URL/+psycopg/}"
if [ -d "$ARQUIVOS" ]; then
  tar -C "$ARQUIVOS" -czf "$DESTINO/documentos-$CARIMBO.tar.gz" .
fi
( cd "$DESTINO" && sha256sum gerenciador-"$CARIMBO".dump $( [ -f "documentos-$CARIMBO.tar.gz" ] && echo "documentos-$CARIMBO.tar.gz" ) > "backup-$CARIMBO.sha256" )
ls -1t "$DESTINO"/gerenciador-*.dump | tail -n +"$(( ${BACKUP_RETENCAO:-14} + 1 ))" | while read -r f; do
  c="${f##*/gerenciador-}"; c="${c%.dump}"; rm -f "$DESTINO"/*"$c"*
done
echo "backup concluído: $DESTINO (carimbo $CARIMBO)"
