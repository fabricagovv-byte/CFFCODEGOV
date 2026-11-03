# Matriz de rastreabilidade — TESTE-001 (FICTÍCIO)

Origem única: prompt mestre do solicitante (Partes 7 e 17). Não há edital real.

| ID | Exigência | Tipo | Documento | Cláusula | Módulo | Evidência esperada | Situação |
|---|---|---|---|---|---|---|---|
| REQ-001 | Login | funcional | Prompt mestre | Parte 7 | MOD-001 | teste `test_login_*` + captura 01 | IMPLEMENTADO |
| REQ-002 | Logout | funcional | Prompt mestre | Parte 7 | MOD-001 | `test_logout_revoga_token` | IMPLEMENTADO |
| REQ-003 | Recuperação de senha | funcional | Prompt mestre | Parte 7 | MOD-001 | `test_recuperacao_*` + captura 03 | IMPLEMENTADO (envio real de e-mail depende de SMTP do órgão) |
| REQ-004 | Perfis e permissões | funcional/segurança | Prompt mestre | Parte 7 | MOD-001 | `test_somente_admin_*`, `test_visibilidade_*` | IMPLEMENTADO |
| REQ-005 | Auditoria | funcional/segurança | Prompt mestre | Partes 7 e 17 | MOD-006 | `test_acoes_sensiveis_sao_auditadas`, trigger PG | IMPLEMENTADO |
| REQ-006 | Cadastro documental | funcional | Prompt mestre | Parte 17 | MOD-002 | `test_mod002_*` + capturas 04–06 | IMPLEMENTADO |
| REQ-007 | Upload de PDF | funcional | Prompt mestre | Parte 17 | MOD-003 | `test_mod003_*` + capturas 07–08 | IMPLEMENTADO |
| REQ-008 | Pesquisa | funcional | Prompt mestre | Parte 17 | MOD-004 | `test_mod004_*` + captura 09 | IMPLEMENTADO |
| REQ-009 | Painel administrativo | funcional | Prompt mestre | Parte 17 | MOD-005 | `test_mod005_*` + captura 10 | IMPLEMENTADO |
| REQ-010 | Infraestrutura e documentação (Docker Compose, manual de publicação) | não funcional | Prompt mestre | Partes 10, 17 | MOD-007 | `verificar_ambiente.sh`, docs/ | IMPLEMENTADO |
| REQ-011 | React + FastAPI + PostgreSQL | tecnologia | Prompt mestre | Parte 7 | todos | código | IMPLEMENTADO |
| REQ-012 | Dados fictícios no preview | LGPD | Prompt de governança | item 7 | MOD-007 | `app/seed.py` | IMPLEMENTADO |
| REQ-013 | Profissional humano responsável | equipe | Prompt mestre | Parte 7 | todos | `RESPONSAVEIS.md` | PENDENTE (a cadastrar) |

## Conflitos entre documentos

Nenhum (fonte única).

## Lacunas

Gestor e fiscal do contrato, preposto, exigências de equipe, ambientes de homologação e produção (ver `fabrica.py contrato faltantes TESTE-001`).
