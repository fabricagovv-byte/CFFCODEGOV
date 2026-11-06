#!/usr/bin/env bash
# Restaura um banco a partir do backup, conferindo o SHA-256 antes.
# Uso: infra/scripts/restore.sh ARQUIVO_DO_BACKUP BANCO_DE_DESTINO
# Pare o sistema antes (docker compose stop comunicacao) e guarde uma cópia do banco atual.
set -euo pipefail
PY="${PYTHON:-python3}"
ARQUIVO="${1:?informe o arquivo do backup}"
DESTINO="${2:?informe o banco de destino}"
PASTA="$(cd "$(dirname "$ARQUIVO")" && pwd)"
NOME="$(basename "$ARQUIVO")"
CARIMBO="${NOME##*-}"; CARIMBO="${CARIMBO%.db}"
HASHES="$PASTA/backup-$CARIMBO.sha256"

[ -f "$HASHES" ] || { echo "erro: lista SHA-256 não encontrada ($HASHES)" >&2; exit 1; }
if ! ( cd "$PASTA" && grep " $NOME\$" "backup-$CARIMBO.sha256" | sha256sum -c --status - ); then
  echo "erro: o SHA-256 de $NOME não confere; o arquivo foi alterado ou corrompido. Nada foi restaurado." >&2
  exit 1
fi

"$PY" - "$PASTA/$NOME" "$DESTINO" <<'PY'
import sqlite3, sys
origem, destino = sys.argv[1], sys.argv[2]
with sqlite3.connect(f"file:{origem}?mode=ro", uri=True) as o:
    if o.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        sys.exit("erro: o arquivo do backup não passou na verificação de integridade do SQLite")
    with sqlite3.connect(destino) as d:
        o.backup(d)
PY
echo "restaurado: $NOME → $DESTINO"
