---
name: gerar-preview
description: GERAR PREVIEW — sobe o sistema localmente com dados fictícios, verifica saúde e captura telas reais com Playwright para as evidências.
---
# GERAR PREVIEW (G07, G11, G12)

1. Suba com Docker (`docker compose up -d --build` na pasta do projeto) ou sem Docker (README do projeto).
2. Carga fictícia: `set -a; . ./.env; set +a; docker compose exec -e ADMIN_EMAIL -e ADMIN_SENHA -e DEMO=1 backend python -m app.seed`.
3. Verifique `/api/health` e `/api/health/db`.
4. Capturas reais: `node fabrica/ferramentas/capturar_telas.mjs <URL> <pasta-evidencias-da-OS> <email> <senha>` (Playwright já instalado no ambiente cloud).
5. Atualize PREVIEW.md de cada módulo: URL real só se publicada; caso contrário "execução local".
