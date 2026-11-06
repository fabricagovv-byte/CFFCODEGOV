---
name: gerar-sistema
description: GERAR SISTEMA / CRIAR SISTEMA / NOVO SISTEMA COM CÓDIGO — o usuário preenche o formulário do sistema (nome, objetivo, módulos e campos) e a fábrica gera o código completo (banco PostgreSQL + migrações, API FastAPI com validação, auditoria e permissão, telas React, testes), roda os testes, faz o build e captura as telas reais (preview).
---
# GERAR SISTEMA (E02 + G06/G07/G08 + G12)

1. Se o usuário ainda não descreveu o sistema, peça para preencher `fabrica/templates/SISTEMA.yaml`
   (exemplo pronto: `fabrica/templates/SISTEMA_EXEMPLO.yaml`). Pergunte só o que faltar: nome, objetivo,
   módulos (o que cada um faz), campos de cada cadastro, quem pode ler/escrever/excluir, item do catálogo de cada módulo.
2. Gere e teste (PostgreSQL real quando houver `TEST_DATABASE_URL`):
   `python3 fabrica/ferramentas/fabrica.py sistema gerar <formulário>`
3. Telas reais com dados fictícios: `python3 fabrica/ferramentas/fabrica.py sistema preview <formulário>`
   (capturas em `projetos/<pasta>/docs/preview/`).
4. Módulos que não são cadastro (relatório, integração, regra especial) saem como "PRECISA DE ESPECIFICAÇÃO":
   use `especificar-modulo` e `plano-implementacao` para eles.
5. Com contrato e OS autorizada: copie `projetos/<pasta>/MODULOS_OS.yaml` para os módulos da OS e siga `fluxo-os`
   (testes → evidências → auditoria → medição → `relatorio tecnico`).
6. Entregue: ZIP do código (`git archive`), telas e o resultado dos testes (código de saída real).
