#!/usr/bin/env bash
# Backup consistente dos bancos (API de backup do SQLite) com SHA-256 e retenção.
# Uso: infra/scripts/backup.sh [DESTINO]            (padrão: ./backups)
# Bancos: DG_COMM_DB e DG_FACTORY_DB (padrão: pastas data/ de cada sistema).
# Em contêiner: veja docs/MANUAL_OPERACAO.md (docker compose cp).
set -euo pipefail
umask 077   # os bancos têm dados pessoais e hashes de senha (LGPD)
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
PY="${PYTHON:-python3}"
DESTINO="${1:-$RAIZ/backups}"
RETENCAO="${BACKUP_RETENCAO:-14}"
COMUNICACAO_DB="${DG_COMM_DB:-$RAIZ/PLATAFORMA_COMUNICACAO/data/comunicacao.db}"
FABRICA_DB="${DG_FACTORY_DB:-$RAIZ/FABRICA/data/factory.db}"
CARIMBO="$(date +%Y%m%dT%H%M%S)"
mkdir -p "$DESTINO"

copiar() {  # copia consistente mesmo com o sistema em uso
  "$PY" - "$1" "$2" <<'PY'
import sqlite3, sys
origem, destino = sys.argv[1], sys.argv[2]
with sqlite3.connect(f"file:{origem}?mode=ro", uri=True) as o, sqlite3.connect(destino) as d:
    o.backup(d)
PY
}

arquivos=()
for par in "comunicacao:$COMUNICACAO_DB" "fabrica:$FABRICA_DB"; do
  nome="${par%%:*}"; banco="${par#*:}"
  if [ -f "$banco" ]; then
    copiar "$banco" "$DESTINO/$nome-$CARIMBO.db"
    arquivos+=("$nome-$CARIMBO.db")
  else
    echo "aviso: banco $nome não encontrado em $banco" >&2
  fi
done
[ ${#arquivos[@]} -gt 0 ] || { echo "erro: nenhum banco copiado" >&2; exit 1; }
( cd "$DESTINO" && sha256sum "${arquivos[@]}" > "backup-$CARIMBO.sha256" )

# Retenção: mantém os $RETENCAO backups mais recentes de cada banco
for nome in comunicacao fabrica; do
  ls -1t "$DESTINO"/"$nome"-*.db 2>/dev/null | tail -n +"$((RETENCAO + 1))" | xargs -r rm -f
done
echo "backup concluído: $DESTINO (${arquivos[*]})"
