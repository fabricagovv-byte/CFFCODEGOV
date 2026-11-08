#!/usr/bin/env bash
# Liga o FreeLLMAPI (IA gratuita por um único endereço) na máquina local, só em 127.0.0.1.
# Uso: bash fabrica/integracoes/freellmapi/iniciar.sh [parar|status]
# Dados, chave de criptografia, senha e chave unificada ficam FORA do git, em $FREELLM_DADOS
# (padrão ~/.fabrica/freellmapi), com permissão 600.
set -euo pipefail

AQUI="$(cd "$(dirname "$0")" && pwd)"
CODIGO="$AQUI/codigo"
DADOS="${FREELLM_DADOS:-$HOME/.fabrica/freellmapi}"
PORTA="${FREELLM_PORTA:-3001}"
URL="http://127.0.0.1:$PORTA"

pid_servidor() {
  for p in /proc/[0-9]*; do
    if [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CODIGO/server" ] && [[ "$(readlink "$p/exe" 2>/dev/null)" == *node* ]]; then
      echo "${p#/proc/}"
    fi
  done
}

case "${1:-}" in
  parar)
    for p in $(pid_servidor); do kill "$p"; done
    echo "FreeLLMAPI parado."; exit 0 ;;
  status)
    if curl -s -m 3 -o /dev/null "$URL/api/auth/status"; then echo "no ar em $URL"; else echo "parado"; fi
    exit 0 ;;
esac

command -v node >/dev/null || { echo "Node.js 20+ é necessário." >&2; exit 1; }
mkdir -p "$DADOS" && chmod 700 "$DADOS"

if [ ! -d "$CODIGO/node_modules" ]; then
  echo "Instalando dependências (uma vez)..."
  (cd "$CODIGO" && npm ci --no-audit --no-fund >/dev/null)
fi
if [ ! -f "$CODIGO/server/dist/index.js" ] || [ ! -f "$CODIGO/client/dist/index.html" ]; then
  echo "Compilando (uma vez)..."
  (cd "$CODIGO" && npm run build >/dev/null)
fi

[ -f "$DADOS/chave_criptografia" ] || { openssl rand -hex 32 > "$DADOS/chave_criptografia"; chmod 600 "$DADOS/chave_criptografia"; }

if ! curl -s -m 3 -o /dev/null "$URL/api/auth/status"; then
  EXTRA=()
  # Ambientes com proxy de saída (ex.: nuvem do Claude Code) precisam do proxy e da CA dele.
  [ -n "${HTTPS_PROXY:-}" ] && EXTRA+=("PROXY_URL=$HTTPS_PROXY")
  [ -f /root/.ccr/ca-bundle.crt ] && EXTRA+=("NODE_EXTRA_CA_CERTS=/root/.ccr/ca-bundle.crt")
  (cd "$CODIGO/server" && env ENCRYPTION_KEY="$(cat "$DADOS/chave_criptografia")" HOST=127.0.0.1 PORT="$PORTA" \
      FREEAPI_DB_PATH="$DADOS/freeapi.db" FREEAPI_BLOCK_PRIVATE_PROVIDER_URLS=false "${EXTRA[@]}" \
      nohup node dist/index.js > "$DADOS/servidor.log" 2>&1 &)
  for _ in $(seq 1 60); do curl -s -m 2 -o /dev/null "$URL/api/auth/status" && break; sleep 0.5; done
fi
curl -s -m 3 -o /dev/null "$URL/api/auth/status" || { echo "Não subiu. Veja $DADOS/servidor.log" >&2; exit 1; }

# Primeira vez: cria a conta do painel e guarda a chave unificada (usada pelos programas).
if curl -s "$URL/api/auth/status" | grep -q '"needsSetup":true'; then
  SENHA="$(openssl rand -hex 12)Aa1"
  printf '%s\n' "$SENHA" > "$DADOS/senha_painel"; chmod 600 "$DADOS/senha_painel"
  TOKEN=$(curl -s -X POST "$URL/api/auth/setup" -H 'content-type: application/json' \
          -d "{\"email\":\"admin@fabrica.local\",\"password\":\"$SENHA\"}" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("token",""))')
  printf '%s\n' "$TOKEN" > "$DADOS/sessao"; chmod 600 "$DADOS/sessao"
  # Provedores gratuitos que funcionam sem chave (limites baixos): Kilo, Pollinations, OVH, AI Horde.
  for p in kilo pollinations ovh aihorde; do
    curl -s -o /dev/null -X POST "$URL/api/keys" -H "authorization: Bearer $TOKEN" -H 'content-type: application/json' \
         -d "{\"platform\":\"$p\",\"label\":\"anonimo\"}"
  done
fi
if [ ! -s "$DADOS/chave_unificada" ]; then
  SENHA="$(cat "$DADOS/senha_painel")"
  TOKEN=$(curl -s -X POST "$URL/api/auth/login" -H 'content-type: application/json' \
          -d "{\"email\":\"admin@fabrica.local\",\"password\":\"$SENHA\"}" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("token",""))')
  curl -s "$URL/api/settings/api-key" -H "authorization: Bearer $TOKEN" \
    | python3 -c 'import json,sys;print(json.load(sys.stdin).get("apiKey",""))' > "$DADOS/chave_unificada"
  chmod 600 "$DADOS/chave_unificada"
fi

echo "FreeLLMAPI no ar em $URL (painel) e $URL/v1 (API compatível com OpenAI e Anthropic)."
echo "Login do painel: admin@fabrica.local — senha em $DADOS/senha_painel"
echo "Chave unificada para os programas: $DADOS/chave_unificada"
echo "Teste: python3 fabrica/ferramentas/fabrica.py ia status"
