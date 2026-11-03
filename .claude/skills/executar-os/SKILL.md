---
name: executar-os
description: EXECUTAR OS / INICIAR DESENVOLVIMENTO — desenvolve uma ordem de serviço AUTORIZADA seguindo o fluxo obrigatório de 15 passos, com código real, testes reais, commits e evidências. Use somente quando a OS tiver autorização registrada.
---
# EXECUTAR OS

Pré-condição: `autorizacao.autorizado: true`, `autorizado_por` e `data` no YAML da OS. Sem isso, pare e registre bloqueio.

Para cada módulo, na ordem das dependências:
1. Analisar requisitos (matriz) → 2. Definir arquitetura (G05) → 3. Criar/ajustar tarefas → 4. Distribuir agentes (mova a tarefa para IN_PROGRESS; a CLI recusa conflito de arquivos).
5. Implementar (G06/G07/G08/G09 ou E04–E13). Cadastros: use a skill gerar-crud (código completo + testes) e depois ajuste as regras do edital. Use worktree/branch separada se dois agentes tocarem o mesmo arquivo.
6. Integrar → 7. Executar testes: `python3 fabrica/ferramentas/fabrica.py testes executar <CONTRATO> <OS> --modulo <MOD>` → 8. Corrigir defeitos.
9. Revisar código (G13/E18; use a skill /code-review quando disponível) → 10. Segurança (G10/E14; /security-review quando disponível).
11. Commit com mensagem clara referenciando OS e módulo → 12. Documentar (preencher ESCOPO, REQUISITOS, ARQUITETURA, SEGURANCA, PREVIEW, IMPLANTACAO do módulo).
13. Preview (skill gerar-preview) → 14. Evidências: `python3 fabrica/ferramentas/fabrica.py evidencias commits <C> <OS>`, `python3 fabrica/ferramentas/fabrica.py testes executar <C> <OS>`, `python3 fabrica/ferramentas/fabrica.py auditar <C> <OS>`.
15. Encaminhar para revisão humana: tarefa em TESTING/IN_REVIEW e mensagem ao G18/G20.

Mova para DONE só com `--resultado` e `--evidencia` reais. Não invente nada.
