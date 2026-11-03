# Gestão Documental Pública — TESTE-001

Sistema de demonstração da OS fictícia **TESTE-001** (medição simulada: 10 UST fictícias).
Cadastro de documentos públicos com upload de PDF, pesquisa, painel administrativo e trilha de auditoria.
**Todos os dados de demonstração são fictícios.**

| Camada | Tecnologia |
|---|---|
| Frontend | React 19 + TypeScript + Vite (servido por Nginx) |
| Backend | Python 3.13 + FastAPI + SQLAlchemy 2 + Alembic |
| Banco | PostgreSQL 16 |
| Infra | Docker Compose; Nginx com TLS para produção |

## Módulos

| Módulo | Escopo | UST (fictícia) |
|---|---|---|
| MOD-001 | Autenticação, logout, recuperação de senha, perfis e permissões | 2 |
| MOD-002 | Cadastro documental (número automático, classificação LAI, arquivamento lógico) | 2 |
| MOD-003 | Upload de PDF (validação de assinatura, limite de tamanho, SHA-256) | 2 |
| MOD-004 | Pesquisa por termos e filtros | 1 |
| MOD-005 | Painel administrativo e gestão de usuários | 1 |
| MOD-006 | Auditoria (somente inserção; trigger no PostgreSQL) | 1 |
| MOD-007 | Infraestrutura e documentação | 1 |

## Opção A — rodar tudo com Docker (recomendado)

```bash
cd projetos/gestao-documental
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
cd projetos/gestao-documental/backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL=sqlite:///./dev.db     # ou postgresql+psycopg2://usuario:senha@localhost:5432/banco
alembic upgrade head
ADMIN_EMAIL=admin@exemplo.gov.br ADMIN_SENHA=SenhaLocal2026 DEMO=1 python -m app.seed
uvicorn app.main:app --reload --port 8000        # API em http://localhost:8000/api/docs

# outro terminal
cd projetos/gestao-documental/frontend
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
