# Código alterado — MOD-003 Base técnica — migrações versionadas, cabeçalhos de segurança, dependências

Gerado a partir do git. Cada linha é um arquivo realmente alterado.

| Commit | Data | Status | Arquivo |
|---|---|---|---|
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/.env.example` |
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/FABRICA/Dockerfile` |
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/Dockerfile` |
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/requirements-dev.txt` |
| `91613ad1a0` | 2026-11-06 | M | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/requirements.txt` |
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/tests/test_backup.py` |
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/README.md` |
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/docker-compose.prod.yml` |
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/docker-compose.yml` |
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/docs/MANUAL_OPERACAO.md` |
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/docs/MANUAL_PUBLICACAO.md` |
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/docs/PLANO_CONTINUIDADE.md` |
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/infra/nginx/default.conf` |
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/infra/nginx/prod-tls.conf` |
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/infra/scripts/backup.sh` |
| `91613ad1a0` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/infra/scripts/restore.sh` |
| `102fc9fd13` | 2026-11-06 | M | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/app/cli.py` |
| `102fc9fd13` | 2026-11-06 | M | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/app/db.py` |
| `102fc9fd13` | 2026-11-06 | M | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/static/style.css` |
| `532d886010` | 2026-11-06 | M | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/README.md` |
| `532d886010` | 2026-11-06 | M | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/app/cli.py` |
| `532d886010` | 2026-11-06 | M | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/app/db.py` |
| `532d886010` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/app/migrations.py` |
| `532d886010` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/migrations/0001_inicial.down.sql` |
| `532d886010` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/migrations/0001_inicial.up.sql` |
| `532d886010` | 2026-11-06 | M | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/requirements.txt` |
| `532d886010` | 2026-11-06 | M | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/static/style.css` |
| `532d886010` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/tests/conftest.py` |
| `532d886010` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/tests/test_mod003_base_tecnica.py` |
| `f823f56b52` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/README.md` |
| `f823f56b52` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/app/cli.py` |
| `f823f56b52` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/app/db.py` |
| `f823f56b52` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/requirements.txt` |
| `f823f56b52` | 2026-11-06 | A | `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/static/style.css` |

## Arquivos atuais do módulo (25)

- `contratos/FIC-COM-2026-001/laboratorio/.env.example`
- `contratos/FIC-COM-2026-001/laboratorio/FABRICA/Dockerfile`
- `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/Dockerfile`
- `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/README.md`
- `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/app/cli.py`
- `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/app/db.py`
- `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/app/migrations.py`
- `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/migrations/0001_inicial.down.sql`
- `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/migrations/0001_inicial.up.sql`
- `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/requirements-dev.txt`
- `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/requirements.txt`
- `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/static/style.css`
- `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/tests/conftest.py`
- `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/tests/test_backup.py`
- `contratos/FIC-COM-2026-001/laboratorio/PLATAFORMA_COMUNICACAO/tests/test_mod003_base_tecnica.py`
- `contratos/FIC-COM-2026-001/laboratorio/README.md`
- `contratos/FIC-COM-2026-001/laboratorio/docker-compose.prod.yml`
- `contratos/FIC-COM-2026-001/laboratorio/docker-compose.yml`
- `contratos/FIC-COM-2026-001/laboratorio/docs/MANUAL_OPERACAO.md`
- `contratos/FIC-COM-2026-001/laboratorio/docs/MANUAL_PUBLICACAO.md`
- `contratos/FIC-COM-2026-001/laboratorio/docs/PLANO_CONTINUIDADE.md`
- `contratos/FIC-COM-2026-001/laboratorio/infra/nginx/default.conf`
- `contratos/FIC-COM-2026-001/laboratorio/infra/nginx/prod-tls.conf`
- `contratos/FIC-COM-2026-001/laboratorio/infra/scripts/backup.sh`
- `contratos/FIC-COM-2026-001/laboratorio/infra/scripts/restore.sh`
