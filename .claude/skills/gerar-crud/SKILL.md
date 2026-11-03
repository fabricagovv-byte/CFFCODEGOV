---
name: gerar-crud
description: GERAR CRUD — gera um cadastro completo e REAL (tabela, migração, API com validação, auditoria e permissão por perfil, tela React com busca e formulário, testes de API e de tela) a partir de uma especificação YAML, separado por módulo, e prova rodando os testes no banco real.
---
# GERAR CRUD (E02 Tech Lead, E04/E05/E06 backend, E08/E09 frontend, G12 testes)

1. Escreva a especificação em `contratos/<ID>/especificacoes/<tabela>.yaml` (modelo e tipos no topo de `fabrica/ferramentas/gerador_crud.py`): entidade, tabela, rotulo, modulo, campos (texto, texto_longo, inteiro, decimal, data, booleano, email, cpf_cnpj, enum, referencia), obrigatório/único/busca/pessoal, permissões por perfil. Campos vêm do edital/TR e do plano — confirme com o usuário.
2. O projeto precisa da base modular (`backend/app/modulos/`; ver MOD-100 do TESTE-002). Gere: `python3 fabrica/ferramentas/fabrica.py crud gerar <spec> --projeto projetos/<sistema>`. Gere primeiro as entidades referenciadas.
3. Prove: `python3 -m pytest` no backend (com `TEST_DATABASE_URL` do PostgreSQL), `alembic check`, `npm run build` e `npx vitest run` no frontend. Corrija o que falhar (no gerador, se for genérico).
4. Revise o código gerado (G13) e ajuste regras de negócio específicas do edital — o gerador entrega a base completa, não substitui a análise.
5. Commit por módulo (`MOD-NNN: ...`), depois evidências: `testes executar` → `evidencias commits` → `auditar` → `medir` → capturas de tela reais.
