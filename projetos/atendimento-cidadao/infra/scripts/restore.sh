#!/usr/bin/env bash
# Restaura banco e arquivos a partir de um carimbo de backup, conferindo o SHA-256.
# Uso: infra/scripts/restore.sh CARIMBO [ORIGEM]
set -euo pipefail
cd "$(dirname "$0")/../.."
CARIMBO="${1:?informe o carimbo, ex.: 20261103T020000}"
ORIGEM="${2:-./backups}"
set -a; [ -f .env ] && . ./.env; set +a
( cd "$ORIGEM" && sha256sum -c "backup-$CARIMBO.sha256" )
docker compose exec -T db pg_restore -U "${POSTGRES_USER:-gd_app}" -d "${POSTGRES_DB:-gestao_documental}" --clean --if-exists --no-owner < "$ORIGEM/banco-$CARIMBO.dump"
docker compose exec -T backend sh -c 'rm -rf /dados/uploads/* && tar -C /dados -xzf -' < "$ORIGEM/uploads-$CARIMBO.tar.gz"
echo "restauração concluída a partir de $CARIMBO"
