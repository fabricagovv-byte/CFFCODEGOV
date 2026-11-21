# Inicia o gerenciador no Windows (PowerShell): carrega o .env, aplica as migrações e sobe o painel na porta 8200.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path .env)) { Write-Host "Crie o arquivo .env a partir do .env.example (veja docs\MANUAL_INSTALACAO.md)"; exit 1 }
Get-Content .env | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object {
    $nome, $valor = $_ -split '=', 2
    Set-Item -Path "env:$nome" -Value $valor
}
if (Test-Path .venv\Scripts\Activate.ps1) { . .venv\Scripts\Activate.ps1 }
Set-Location backend
alembic upgrade head
$porta = if ($env:PORTA) { $env:PORTA } else { "8200" }
uvicorn app.main:app --host 127.0.0.1 --port $porta
