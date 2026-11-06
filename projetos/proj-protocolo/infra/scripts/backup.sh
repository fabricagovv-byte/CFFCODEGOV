#!/usr/bin/env bash
# Backup do banco do projeto (pg_dump, formato custom) com SHA-256 e retenção.
# Uso: infra/scripts/backup.sh [DESTINO]   (lê DATABASE_URL do .env)
set -euo pipefail
umask 077
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
set -a; [ -f "$RAIZ/.env" ] && . "$RAIZ/.env"; set +a
DESTINO="${1:-$RAIZ/backups}"
URL="${DATABASE_URL/+psycopg/}"
CARIMBO="$(date +%Y%m%dT%H%M%S)"
mkdir -p "$DESTINO"
pg_dump --format=custom --no-owner --file "$DESTINO/proj-protocolo-$CARIMBO.dump" "$URL"
( cd "$DESTINO" && sha256sum "proj-protocolo-$CARIMBO.dump" > "proj-protocolo-$CARIMBO.sha256" )
ls -1t "$DESTINO"/proj-protocolo-*.dump | tail -n +"$(( ${BACKUP_RETENCAO:-14} + 1 ))" | while read -r f; do rm -f "$f" "${f%.dump}.sha256"; done
echo "backup concluído: $DESTINO/proj-protocolo-$CARIMBO.dump"
