# Biblioteca de conhecimento da fábrica

Material externo **fornecido pelo usuário** (03/11/2026), lido integralmente nas partes usadas e incorporado com a licença original.
Só textos (`.md`) e exemplos; scripts executáveis e servidores dos pacotes originais **não** foram copiados.

| Origem | Licença | O que guardamos aqui | Onde virou regra/skill da fábrica |
|---|---|---|---|
| obra/superpowers | MIT (`superpowers/LICENSE`) | 13 skills de disciplina de engenharia | `verificar-antes-de-concluir`, `tdd`, `depuracao-sistematica`, `plano-implementacao`, `executar-plano`, `revisao-de-codigo`, `trabalho-paralelo`, `concluir-entrega` |
| github/spec-kit | MIT (`spec-kit/LICENSE`) | método Spec-Driven Development + modelos (spec, plan, tasks, checklist, constitution, comandos) | `especificar-modulo` (spec → esclarecer → plano → tarefas → analisar) |
| anthropics/skills (Apache 2.0) | Apache 2.0 (`LICENSE.txt` em cada pasta) | webapp-testing, skill-creator, frontend-design, mcp-builder, internal-comms | `testar-webapp`, `criar-skill`, `design-de-interface`, `integracao-mcp`, relatórios de status |
| langchain-ai/langgraph | MIT (`langgraph/LICENSE`) | conceitos (sem código) — `langgraph/CONCEITOS.md` | `fabrica.py fluxo` (pipeline em grafo com pontos de retomada e pausas humanas) |

**Não incorporado:**
- `docx`, `pdf`, `pptx`, `xlsx` da Anthropic: licença "todos os direitos reservados", não redistribuível. A fábrica usa seu próprio gerador de Word (`word.cjs`).
- `using-superpowers` e `diagnosing-superpowers`: específicos do plugin original. O primeiro obriga a acionar skills antes de qualquer resposta, o que conflitaria com o fluxo da fábrica.
- Skills criativas (arte, GIF, temas, marca): fora do escopo de contratos públicos.

As skills da fábrica são **adaptações em português**, ligadas às regras do `AGENTS.md`. Quando precisar do detalhe completo, leia o original nesta pasta.
