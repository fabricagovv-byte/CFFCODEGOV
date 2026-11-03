#!/usr/bin/env bash
# Backup do banco (pg_dump formato custom) e dos arquivos PDF, com hash SHA-256.
# Uso: infra/scripts/backup.sh [DESTINO]   (padrão: ./backups)
set -euo pipefail
umask 077   # backups contêm dados pessoais e hashes de senha (LGPD)
cd "$(dirname "$0")/../.."
DESTINO="${1:-./backups}"
CARIMBO="$(date +%Y%m%dT%H%M%S)"
mkdir -p "$DESTINO"
set -a; [ -f .env ] && . ./.env; set +a
docker compose exec -T db pg_dump -U "${POSTGRES_USER:-gd_app}" -d "${POSTGRES_DB:-gestao_documental}" -Fc > "$DESTINO/banco-$CARIMBO.dump"
docker compose exec -T backend tar -C /dados -czf - uploads > "$DESTINO/uploads-$CARIMBO.tar.gz"
# Criptografia opcional: defina BACKUP_GPG_DESTINATARIO (chave pública do órgão).
if [ -n "${BACKUP_GPG_DESTINATARIO:-}" ]; then
  for f in "$DESTINO/banco-$CARIMBO.dump" "$DESTINO/uploads-$CARIMBO.tar.gz"; do
    gpg --batch --yes --encrypt --recipient "$BACKUP_GPG_DESTINATARIO" --output "$f.gpg" "$f" && shred -u "$f"
  done
  echo "AVISO: arquivos criptografados (.gpg); descriptografe antes de usar restore.sh"
  exit 0
fi
( cd "$DESTINO" && sha256sum "banco-$CARIMBO.dump" "uploads-$CARIMBO.tar.gz" > "backup-$CARIMBO.sha256" )
# Retenção: mantém os 14 backups mais recentes (ajuste conforme política do órgão)
ls -1t "$DESTINO"/banco-*.dump 2>/dev/null | tail -n +15 | while read -r f; do c="${f##*/banco-}"; c="${c%.dump}"; rm -f "$DESTINO"/*"$c"*; done
echo "backup concluído: $DESTINO (*-$CARIMBO)"
