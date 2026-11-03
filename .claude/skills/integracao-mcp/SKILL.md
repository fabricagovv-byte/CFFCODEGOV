---
name: integracao-mcp
description: Use quando o edital exigir integração com sistemas ou quando a fábrica precisar de uma ferramenta nova via MCP (Model Context Protocol) - planejar, implementar e avaliar um servidor MCP ou cliente de API com tratamento de falhas.
---
# Integrações e servidores MCP

Adaptado de anthropics/skills mcp-builder (Apache 2.0) — original em `fabrica/conhecimento/anthropic-skills/mcp-builder/` (guias de boas práticas, Python e TypeScript).

1. Entenda a API externa (documentação oficial do órgão/sistema), autenticação e limites. Registre a origem no edital.
2. Desenhe ferramentas pelo fluxo de trabalho (não 1:1 com endpoints), nomes claros, respostas concisas, erros que orientam a correção.
3. Implemente (Python/FastMCP ou TypeScript), com timeout, retentativa idempotente e logs sem dados pessoais.
4. Teste com dublê/sandbox; crie avaliações com perguntas reais.
5. Credenciais só em variáveis de ambiente/cofre do órgão — nunca no git.
