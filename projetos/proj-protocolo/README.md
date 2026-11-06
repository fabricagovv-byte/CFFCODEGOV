# Protocolo Digital (exemplo)

Projeto `proj-protocolo` da Fábrica DigitalGov, com banco de dados próprio (`proj_protocolo`).

| Camada | Onde está |
|---|---|
| Banco de dados | `backend/migrations/` (Alembic) e `backend/app/modelos.py` |
| Back-end | `backend/app/` (FastAPI) |
| Front-end | `frontend/` |
| Testes | `backend/tests/` |
| Backup | `infra/scripts/backup.sh` e `restore.sh` |

## Rodar

Linux/macOS:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r backend/requirements-dev.txt
set -a && . ./.env && set +a
cd backend && alembic upgrade head && uvicorn app.main:app --port 8100
```

Windows (PowerShell):

```powershell
py -3 -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r backend\requirements-dev.txt
Get-Content .env | Where-Object { $_ -match '^[A-Z_]+=' } | ForEach-Object { $n,$v = $_ -split '=',2; Set-Item "env:$n" $v }
cd backend; alembic upgrade head; uvicorn app.main:app --port 8100
```

Abra http://127.0.0.1:8100, grave um registro e veja que ele aparece na lista: é a prova de que a tela, a API e o banco estão ligados.

## Testes

```bash
cd backend && python -m pytest -q
```
