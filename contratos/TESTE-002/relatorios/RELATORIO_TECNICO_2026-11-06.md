# Relatório Técnico de Execução e Medição — novembro de 2026

## 1. Resumo

- **Contratado:** 300 UST.
- **Feito e comprovado (acumulado):** 80,4 UST em 3 módulo(s) — 26,8% do contratado.
- **Feito em novembro de 2026:** 80,4 UST em 3 módulo(s).
- **Feito hoje (06/11/2026):** 0 UST.
- **Aceito pelo órgão:** 0 UST — aguardando documento de aceite do fiscal/gestor.
- **Saldo do contrato:** 219,6 UST (contratado − comprovado); 300 UST considerando só o aceito.
- **A fazer (planejado):** 2 módulo(s), cerca de 29,4 UST (estimativa pelo catálogo).

| Indicador | UST | % do contratado |
|---|---|---|
| Contratado | 300 | 100% |
| Previsto nas OS | 80,4 | 26,8% |
| Comprovado (feito, testado e auditado) | 80,4 | 26,8% |
| Aceito pelo órgão | 0 | 0% |
| A fazer (estimativa) | 29,4 | 9,8% |
| Saldo (contratado − comprovado) | 219,6 | 73,2% |

> Comprovado = entregue com código no repositório, testes executados e evidências auditadas, medido pelo catálogo do contrato. Só passa a **aceito** com documento do órgão (termo, ofício ou e-mail do fiscal).
> OS-TESTE-002: UST FICTÍCIAS — catálogo, perfis e valores de demonstração; sem valor para faturamento.

## 2. Identificação

| Campo | Informação |
|---|---|
| Órgão | Órgão Fictício de Demonstração |
| Contrato | TESTE-002 |
| Objeto | Atendimento ao cidadão e protocolo (demonstração da fábrica — FICTÍCIO) |
| Ordens de serviço | OS-TESTE-002 — Projeto ATENDIMENTO — interessados e protocolos |
| Sistema(s) | projetos/gestao-documental |
| Período | novembro de 2026 (até 06/11/2026) |
| Contratada | V4 Tecnologia Brasil · DigitalGov — CNPJ 24.361.188/0001-61 |
| Responsável técnico | Warley Luciano Costa Gomes |

## 3. O que foi feito e quanto foi medido

| Módulo | O que foi entregue | Item do contrato | UST comprovada | Testes |
|---|---|---|---|---|
| MOD-100 — Base modular para cadastros | API e regras de negócio, Banco de dados, Testes automatizados, Telas | SRV-BASE | 12,2 | 105 ok, 0 falha(s) |
| MOD-101 — Cadastro de interessados | API e regras de negócio, Banco de dados, Testes automatizados, Telas | SRV-CRUD-M | 24,4 | 17 ok, 0 falha(s) |
| MOD-102 — Cadastro de protocolos | API e regras de negócio, Banco de dados, Testes automatizados, Telas | SRV-CRUD-A | 43,8 | 18 ok, 0 falha(s) |
| **Total** | | | **80,4** | |

### MOD-100 — Base modular para cadastros

- **Banco de dados:** estrutura e acesso a dados — 1 arquivo(s), 32 linhas.
- **API (backend):** 2 rota(s): `GET /api/health`, `GET /api/health/db` — 4 arquivo(s), 190 linhas.
- **Telas (frontend):** App — 1 arquivo(s), 62 linhas.
- **Testes:** 105 executado(s), 0 falha(s) — APROVADO em 2026-11-03 (2 arquivo(s) de teste, 134 linhas).
- **Medição:** item SRV-BASE — SRV-BASE × 1 (Estrutura base de módulos (FICTÍCIO); Catálogo fictício item 1): previsto 12,2, comprovado **12,2**, aceito 0 UST; 10 h pelo catálogo.
- **Commits:** `ea7f8f4` 2026-11-03 MOD-100: base modular — descoberta automática de módulos, validadores CPF/CNPJ e permissão por perfil; `e4e16a3` 2026-11-03 MOD-007: infraestrutura (Docker Compose, Nginx/TLS, backup/restauração), base da API, migrações e documentação.
- **Responsável:** A CADASTRAR.

### MOD-101 — Cadastro de interessados

- **Banco de dados:** tabela(s) `interessados` — 2 arquivo(s), 59 linhas.
- **API (backend):** 5 rota(s): `GET /api/interessados`, `GET /api/interessados/{rid}`, `POST /api/interessados`, `PATCH /api/interessados/{rid}`, `DELETE /api/interessados/{rid}` — 3 arquivo(s), 198 linhas.
- **Telas (frontend):** InteressadoPagina — 2 arquivo(s), 124 linhas.
- **Testes:** 17 executado(s), 0 falha(s) — APROVADO em 2026-11-03 (2 arquivo(s) de teste, 149 linhas).
- **Medição:** item SRV-CRUD-M — SRV-CRUD-M × 1 (Cadastro completo média complexidade (FICTÍCIO); Catálogo fictício item 2): previsto 24,4, comprovado **24,4**, aceito 0 UST; 24 h pelo catálogo.
- **Commits:** `83e7978` 2026-11-03 MOD-101: cadastro de interessados (gerado da especificação: modelo, migração, API, auditoria, tela e testes).
- **Responsável:** A CADASTRAR.

![MOD-101 — validacao cpf invalido (preview)](../evidencias/OS-TESTE-002/MOD-101/SCREENSHOTS/01-validacao-cpf-invalido.png)

![MOD-101 — interessados lista (preview)](../evidencias/OS-TESTE-002/MOD-101/SCREENSHOTS/02-interessados-lista.png)

### MOD-102 — Cadastro de protocolos

- **Banco de dados:** tabela(s) `protocolos` — 2 arquivo(s), 66 linhas.
- **API (backend):** 5 rota(s): `GET /api/protocolos`, `GET /api/protocolos/{rid}`, `POST /api/protocolos`, `PATCH /api/protocolos/{rid}`, `DELETE /api/protocolos/{rid}` — 3 arquivo(s), 197 linhas.
- **Telas (frontend):** ProtocoloPagina — 2 arquivo(s), 131 linhas.
- **Testes:** 18 executado(s), 0 falha(s) — APROVADO em 2026-11-03 (2 arquivo(s) de teste, 161 linhas).
- **Medição:** item SRV-CRUD-A — SRV-CRUD-A × 1 (Cadastro completo alta complexidade com relacionamentos (FICTÍCIO); Catálogo fictício item 3): previsto 43,8, comprovado **43,8**, aceito 0 UST; 36 h pelo catálogo.
- **Commits:** `6e7928a` 2026-11-03 MOD-102: lista mostra o nome do interessado; mensagens de validação sem prefixo técnico (gerador corrigido); `7313248` 2026-11-03 MOD-102: cadastro de protocolos com relacionamento a interessados (gerado da especificação).
- **Responsável:** A CADASTRAR.

![MOD-102 — protocolo formulario (preview)](../evidencias/OS-TESTE-002/MOD-102/SCREENSHOTS/01-protocolo-formulario.png)

![MOD-102 — protocolos busca (preview)](../evidencias/OS-TESTE-002/MOD-102/SCREENSHOTS/02-protocolos-busca.png)

## 4. Tecnologias utilizadas

| Camada | Tecnologias | Fonte |
|---|---|---|
| Exigidas no contrato | React, FastAPI, PostgreSQL | `contrato.yaml` |
| Banco de dados | PostgreSQL 16 | `contrato.yaml` |
| Backend (Python) | fastapi, uvicorn, sqlalchemy, alembic, psycopg2-binary, pydantic, python-multipart, bcrypt, pyjwt | `projetos/gestao-documental/backend/requirements.txt` |
| Frontend (TypeScript/React) | react, react-dom, react-router-dom | `projetos/gestao-documental/frontend/package.json` |
| Build e testes de tela | @testing-library/dom, @testing-library/react, @testing-library/user-event, @types/node, @types/react, @types/react-dom, @vitejs/plugin-react, jsdom, typescript, vite, vitest | `projetos/gestao-documental/frontend/package.json` |
| Infraestrutura (contêineres) | nginx:1.27-alpine | `projetos/gestao-documental/docker-compose.prod.yml` |
| Infraestrutura (contêineres) | postgres:16-alpine | `projetos/gestao-documental/docker-compose.yml` |

## 5. Código de novembro de 2026

**projetos/gestao-documental:** 11 commit(s), +4832 / −3 linhas.

| Camada | Arquivos alterados | Linhas adicionadas | Linhas removidas |
|---|---|---|---|
| API e regras de negócio (backend) | 31 | 1479 | 0 |
| Telas (frontend) | 29 | 1129 | 2 |
| Testes automatizados | 22 | 1050 | 1 |
| Banco de dados | 13 | 540 | 0 |
| Infraestrutura (Docker, proxy, CI) | 12 | 309 | 0 |
| Documentação | 6 | 276 | 0 |
| Especificação | 2 | 27 | 0 |
| Outros | 2 | 22 | 0 |

| Commit | Data | Descrição |
|---|---|---|
| `6e7928a` | 2026-11-03 | MOD-102: lista mostra o nome do interessado; mensagens de validação sem prefixo técnico (gerador corrigido) |
| `7313248` | 2026-11-03 | MOD-102: cadastro de protocolos com relacionamento a interessados (gerado da especificação) |
| `83e7978` | 2026-11-03 | MOD-101: cadastro de interessados (gerado da especificação: modelo, migração, API, auditoria, tela e testes) |
| `ea7f8f4` | 2026-11-03 | MOD-100: base modular — descoberta automática de módulos, validadores CPF/CNPJ e permissão por perfil |
| `e10e719` | 2026-11-03 | MOD-006: trilha de auditoria somente inserção e tela de consulta |
| `3cbdf19` | 2026-11-03 | MOD-005: painel administrativo com indicadores e gestão de usuários |
| `0ca859e` | 2026-11-03 | MOD-004: pesquisa por termos e filtros respeitando classificação |
| `348ec80` | 2026-11-03 | MOD-003: upload de PDF com validação de assinatura, limite e SHA-256 |
| `e419dae` | 2026-11-03 | MOD-002: cadastro documental com classificação LAI e arquivamento lógico |
| `0c1c851` | 2026-11-03 | MOD-001: autenticação, logout, recuperação de senha, perfis e permissões |
| `e4e16a3` | 2026-11-03 | MOD-007: infraestrutura (Docker Compose, Nginx/TLS, backup/restauração), base da API, migrações e documentação |

### Código de hoje (06/11/2026)

**projetos/gestao-documental:** 0 commit(s), +0 / −0 linhas.

## 6. Código total do sistema

**projetos/gestao-documental:** 110 arquivo(s), 4829 linhas, 11 commit(s) desde o início.

| Camada | Arquivos | Linhas |
|---|---|---|
| API e regras de negócio (backend) | 29 | 1479 |
| Telas (frontend) | 26 | 1127 |
| Testes automatizados | 21 | 1049 |
| Banco de dados | 12 | 540 |
| Infraestrutura (Docker, proxy, CI) | 12 | 309 |
| Documentação | 6 | 276 |
| Especificação | 2 | 27 |
| Outros | 2 | 22 |

| Linguagem | Arquivos | Linhas |
|---|---|---|
| Python | 48 | 2765 |
| TypeScript (React) | 26 | 1056 |
| Markdown | 6 | 276 |
| TypeScript | 5 | 183 |
| Configuração | 5 | 163 |
| YAML | 4 | 98 |
| Shell | 3 | 70 |
| CSS | 1 | 57 |
| Outros | 5 | 53 |
| JSON | 2 | 49 |
| Docker | 2 | 34 |
| HTML | 1 | 13 |
| Texto | 2 | 12 |

> Linhas de código e commits mostram o tamanho do trabalho; a quantidade medida vem do catálogo do contrato, não das linhas.

## 7. A fazer e saldo

| Módulo | O que fazer | Item do contrato | UST (estimativa) | Prazo | Responsável |
|---|---|---|---|---|---|
| MOD-201 | Relatório de protocolos por período | SRV-REL | 14,7 | 2026-11-11 | a definir |
| MOD-202 | Relatório de atendimento por canal | SRV-REL | 14,7 | 2026-11-12 | a definir |

| Saldo | UST |
|---|---|
| Contratado | 300 |
| (−) Comprovado | 80,4 |
| (=) Saldo atual | 219,6 |
| (−) A fazer (estimativa) | 29,4 |
| (=) Saldo depois do planejado | 190,2 |

## 8. Pendências

- Aceite do órgão para 80,4 UST comprovadas (termo, ofício ou e-mail do fiscal).
- Responsável humano não registrado em: MOD-100, MOD-101, MOD-102.

## 9. Fonte dos números

- UST: `medicoes/<OS>.json` (medição pelo catálogo do contrato) e `contrato.yaml`.
- O que foi feito, código e commits: repositório git (`git log`, `git ls-files`).
- Testes: `evidencias/<OS>/<MÓDULO>/TESTES.json` (execuções reais com JUnit).
- Telas: capturas reais em `evidencias/<OS>/<MÓDULO>/SCREENSHOTS/`.
- A fazer: `PLANEJAMENTO.csv` (estimativa pelo catálogo).

