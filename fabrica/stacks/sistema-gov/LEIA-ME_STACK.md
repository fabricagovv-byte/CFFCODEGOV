# Stack sistema-gov — base completa de sistema público

Ponto de partida real (vem do sistema do TESTE-001/TESTE-002, já testado): FastAPI + SQLAlchemy + Alembic + PostgreSQL,
React + TypeScript, login com JWT e logout, recuperação de senha, perfis (ADMIN/GESTOR/OPERADOR/CONSULTA), usuários,
trilha de auditoria imutável, documentos com PDF, pesquisa, painel, Docker Compose, Nginx/TLS, backup/restauração e
**base modular** para cadastros gerados com `fabrica.py crud gerar` (cada cadastro em pasta própria, com testes).

Remova o que o seu sistema não usar (ex.: módulo de documentos) — os testes mostram o que depende de quê.
