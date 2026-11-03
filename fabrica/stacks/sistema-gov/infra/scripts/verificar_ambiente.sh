#!/usr/bin/env bash
# Verificação ponta a ponta do ambiente Docker: saúde, migração, carga, backup e restauração.
# Uso: infra/scripts/verificar_ambiente.sh   (com a stack no ar)
set -euo pipefail
cd "$(dirname "$0")/../.."
set -a; . ./.env; set +a
URL="http://localhost:${PORTA_HTTP:-8080}"
passo(){ echo; echo "== $* ($(date -Iseconds))"; }
passo "Contêineres"; docker compose ps --format '{{.Service}} {{.State}} {{.Health}}'
passo "Saúde da API"; curl -fsS "$URL/api/health"; echo; curl -fsS "$URL/api/health/db"; echo
passo "Migração aplicada"; docker compose exec -T backend alembic current 2>&1 | grep -v JWT_SECRET
passo "Carga fictícia"; docker compose exec -T -e ADMIN_EMAIL -e ADMIN_SENHA -e DEMO=1 backend python -m app.seed
passo "Login pelo proxy do frontend"
TOKEN=$(curl -fsS -X POST "$URL/api/auth/login" -H 'Content-Type: application/json' \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"senha\":\"$ADMIN_SENHA\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
echo "token obtido (${#TOKEN} caracteres)"
ANTES=$(curl -fsS "$URL/api/painel/resumo" -H "Authorization: Bearer $TOKEN" | python3 -c 'import sys,json;print(json.load(sys.stdin)["documentos_total"])')
echo "documentos antes do backup: $ANTES"
passo "Trigger de auditoria imutável"
SAIDA=$(docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "DELETE FROM auditoria" 2>&1 || true)
echo "$SAIDA" | grep -q "somente inserção" && echo "bloqueado: $(echo "$SAIDA" | grep -o 'somente inserção.*')" || { echo "FALHA: DELETE não foi bloqueado"; exit 1; }
passo "Backup"; infra/scripts/backup.sh ./backups | tail -1
CARIMBO=$(ls -1t backups/banco-*.dump | head -1 | sed 's/.*banco-\(.*\)\.dump/\1/')
passo "Simulando perda: criando documento extra após o backup"
curl -fsS -X POST "$URL/api/documentos" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"titulo":"Documento criado após o backup","tipo":"Ofício"}' >/dev/null
DEPOIS=$(curl -fsS "$URL/api/painel/resumo" -H "Authorization: Bearer $TOKEN" | python3 -c 'import sys,json;print(json.load(sys.stdin)["documentos_total"])')
echo "documentos após inclusão: $DEPOIS"
passo "Restauração do backup $CARIMBO"; infra/scripts/restore.sh "$CARIMBO" ./backups 2>&1 | tail -2
TOKEN=$(curl -fsS -X POST "$URL/api/auth/login" -H 'Content-Type: application/json' \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"senha\":\"$ADMIN_SENHA\"}" | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
RESTAURADO=$(curl -fsS "$URL/api/painel/resumo" -H "Authorization: Bearer $TOKEN" | python3 -c 'import sys,json;print(json.load(sys.stdin)["documentos_total"])')
echo "documentos após restauração: $RESTAURADO (esperado: $ANTES)"
[ "$RESTAURADO" = "$ANTES" ] && echo "RESULTADO: APROVADO" || { echo "RESULTADO: REPROVADO"; exit 1; }
