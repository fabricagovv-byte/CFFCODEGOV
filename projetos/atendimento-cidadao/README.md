# Atendimento ao Cidadão

Registrar cidadãos, unidades de atendimento e solicitações, com protocolo, prazo e situação.

- Órgão: Órgão de demonstração (fictício)
- Contrato: a definir
- Usuários: atendentes, gestores e consulta

| Camada | Tecnologia |
|---|---|
| Frontend | React + TypeScript + Vite (servido por Nginx) |
| Backend | Python + FastAPI + SQLAlchemy 2 + Alembic |
| Banco | PostgreSQL 16 |
| Infra | Docker Compose; Nginx com TLS para produção |

## Módulos

| Módulo | O que faz | Situação |
|---|---|---|
| Base | Login, perfis, usuários, auditoria, documentos, pesquisa e painel | pronta (stack sistema-gov) |
| MOD-101 — Unidades de atendimento | cadastro das unidades onde o cidadão é atendido | GERADO |
| MOD-102 — Cidadãos | cadastro dos cidadãos atendidos, com CPF validado | GERADO |
| MOD-103 — Solicitações | registro das solicitações do cidadão com protocolo, canal, prazo e situação | GERADO |
| MOD-104 — Relatório de atendimentos por período | total de solicitações por unidade, canal e situação no período | PRECISA DE ESPECIFICAÇÃO (não é cadastro: relatório, integração ou regra especial) |

Formulário de origem: `SISTEMA.yaml`. Detalhes e testes: `docs/MODULOS.md`. Telas: `docs/PREVIEW.md`.

## Opção A — rodar tudo com Docker (recomendado)

```bash
cd projetos/atendimento-cidadao
cp .env.example .env            # edite e TROQUE todos os valores
docker compose up -d --build    # sobe banco, API (aplica migrações) e frontend
set -a; . ./.env; set +a        # carrega ADMIN_EMAIL/ADMIN_SENHA no shell
docker compose exec -e ADMIN_EMAIL -e ADMIN_SENHA -e DEMO=1 backend python -m app.seed   # admin + dados fictícios
# abra http://localhost:8080  (login: ADMIN_EMAIL / ADMIN_SENHA do .env)
```

Usuários fictícios criados com `DEMO=1` (mesma senha do admin): `gestor@demo.gov.br`, `operador@demo.gov.br`, `consulta@demo.gov.br`.

## Opção B — rodar sem Docker (desenvolvimento)

```bash
# Banco: PostgreSQL local ou SQLite (padrão, para testes rápidos)
cd projetos/atendimento-cidadao/backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL=sqlite:///./dev.db     # ou postgresql+psycopg2://usuario:senha@localhost:5432/banco
alembic upgrade head
ADMIN_EMAIL=admin@exemplo.gov.br ADMIN_SENHA=SenhaLocal2026 DEMO=1 python -m app.seed
uvicorn app.main:app --reload --port 8000        # API em http://localhost:8000/api/docs

# outro terminal
cd projetos/atendimento-cidadao/frontend
npm ci && npm run dev                            # http://localhost:5173 (proxy /api -> :8000)
```

## Testes

```bash
cd backend && python3 -m pytest                       # SQLite
TEST_DATABASE_URL=postgresql+psycopg2://u:s@localhost:5432/banco_teste python3 -m pytest   # PostgreSQL real
cd ../frontend && npm test && npm run build
```

## Documentação

- [Arquitetura](docs/ARQUITETURA.md)
- [Manual de publicação (passo a passo)](docs/MANUAL_PUBLICACAO.md)
- [Manual de operação e manutenção](docs/MANUAL_OPERACAO.md)
- [Plano de continuidade e recuperação de desastres](docs/PLANO_CONTINUIDADE.md)
- [Segurança e LGPD](docs/SEGURANCA_LGPD.md)
- [Preview](docs/PREVIEW.md)
- API interativa: `/api/docs` (OpenAPI em `/api/openapi.json`)
