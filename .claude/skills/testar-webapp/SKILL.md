---
name: testar-webapp
description: Use para testar a interface web de verdade (Playwright) - subir o sistema, navegar, preencher formulários, conferir mensagens, capturar telas como evidência e investigar falhas de tela.
---
# Testar a aplicação web

Adaptado de anthropics/skills webapp-testing (Apache 2.0) — original em `fabrica/conhecimento/anthropic-skills/webapp-testing/`.

1. Suba o sistema (Docker Compose ou backend+frontend local) e confirme `/api/health`.
2. Reconhecimento primeiro: abra a página, espere carregar (`networkidle`/elemento visível), capture a tela, descubra seletores por **papel e rótulo** (`getByRole`, `getByLabel`) — isso também valida acessibilidade.
3. Roteiro real: login → navegar → criar registro → validar erro (ex.: CPF inválido) → buscar → excluir. Uma captura por passo relevante.
4. Capturas vão para `evidencias/<OS>/<MOD>/SCREENSHOTS/` (modelo: `fabrica/ferramentas/capturar_telas.cjs`, `contratos/TESTE-002/capturar_telas_teste002.cjs`).
5. Falhou? skill depuracao-sistematica; console do navegador e resposta da API.
