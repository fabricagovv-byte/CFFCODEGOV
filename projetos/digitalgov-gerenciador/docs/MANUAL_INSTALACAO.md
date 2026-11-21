# Manual de instalação

Este manual instala o gerenciador num computador ou servidor. Os comandos aparecem em duas versões: **Windows** (PowerShell) e **Linux** (Ubuntu). Use só a do seu sistema.

## 1. Instalar as ferramentas

Você precisa de três programas: **Python 3.12 ou mais novo**, **PostgreSQL 16** e **Git**.

### Windows

1. **Python:** abra https://www.python.org/downloads/ e clique em *Download Python 3.13*. Ao abrir o instalador, **marque a caixa "Add python.exe to PATH"** (fica embaixo, na primeira tela) e clique em *Install Now*.
2. **PostgreSQL:** abra https://www.postgresql.org/download/windows/ → *Download the installer* → escolha a versão 16 para Windows x86-64. No instalador:
   - deixe marcados *PostgreSQL Server*, *pgAdmin 4* e *Command Line Tools*;
   - quando pedir a **senha do superusuário (postgres)**, crie uma senha forte e guarde-a num gerenciador de senhas;
   - porta: deixe **5432**.
3. **Git:** abra https://git-scm.com/download/win e instale com as opções padrão.

**Onde executar os comandos:** clique no menu Iniciar, digite **PowerShell** e abra o *Windows PowerShell*. Todos os comandos Windows deste manual são digitados ali.

Confirme que deu certo (cada comando deve mostrar uma versão):

```powershell
python --version
git --version
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" --version
```

Para não digitar o caminho do `psql` toda vez, rode uma vez:

```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\PostgreSQL\16\bin", "User")
```

Feche e abra o PowerShell de novo; depois disso `psql --version` funciona direto.

### Linux (Ubuntu 22.04 ou 24.04)

**Onde executar os comandos:** abra o *Terminal* (Ctrl+Alt+T).

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git postgresql postgresql-client
python3 --version && git --version && psql --version
```

## 2. Baixar o código

Escolha uma pasta de trabalho (no Windows, por exemplo, `C:\digitalgov`; no Linux, `~/digitalgov`).

Windows:

```powershell
mkdir C:\digitalgov; cd C:\digitalgov
git clone https://github.com/fabricagovv-byte/cffcodegov.git
cd cffcodegov\projetos\digitalgov-gerenciador
```

Linux:

```bash
mkdir -p ~/digitalgov && cd ~/digitalgov
git clone https://github.com/fabricagovv-byte/cffcodegov.git
cd cffcodegov/projetos/digitalgov-gerenciador
```

(Se recebeu o ZIP do gerenciador, descompacte-o e entre na pasta `digitalgov-gerenciador`.)

## 3. Criar o banco central

Siga o **passo 2 do `docs/MANUAL_BANCO_DE_DADOS.md`** (cria o usuário `gerenciador_app` e o banco `digitalgov_gerenciador`). Volte aqui depois.

## 4. Instalar as bibliotecas do Python

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements-dev.txt
```

Se o PowerShell recusar o `Activate.ps1` com "execução de scripts desabilitada", rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e tente de novo.

Linux:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements-dev.txt
```

## 5. Configurar as credenciais com segurança

1. Copie o modelo: Windows `copy .env.example .env` · Linux `cp .env.example .env`.
2. Abra o `.env` num editor (Windows: `notepad .env`; Linux: `nano .env`).
3. Na linha `GERENCIADOR_DATABASE_URL`, troque `SENHA` pela senha do usuário `gerenciador_app` criada no passo 3.
4. Salve. No Linux, proteja o arquivo: `chmod 600 .env`.

Regras: o `.env` **nunca** vai para o GitHub (ele já está no `.gitignore`), não é enviado por e-mail ou WhatsApp e não aparece em relatórios. Quem precisar da senha recebe pelo gerenciador de senhas.

## 6. Criar as tabelas (migrações) e o administrador

Windows:

```powershell
Get-Content .env | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object { $n,$v = $_ -split '=',2; Set-Item "env:$n" $v }
cd backend
alembic upgrade head
python -m app.cli criar-admin --nome "Seu Nome" --login admin
cd ..
```

Linux:

```bash
set -a && . ./.env && set +a
cd backend
alembic upgrade head
python -m app.cli criar-admin --nome "Seu Nome" --login admin
cd ..
```

O comando pede a senha do administrador (mínimo 12 caracteres) sem mostrá-la na tela.

**Confirme:** `alembic current` (dentro de `backend`) deve mostrar `0001 (head)`.

## 7. Cadastrar a equipe e os agentes (opcional, por arquivo)

A equipe pode ser cadastrada pela tela *Profissionais* ou importada de um CSV com as colunas `nome` e `funcao`:

```bash
python -m app.cli importar-profissionais ../../../contratos/FIC-COM-2026-001/PROFISSIONAIS.csv
python -m app.cli importar-agentes ../../../fabrica/agentes/registry.yaml
```

CPF completo nunca é importado: só o formato mascarado `***.456.789-**`.

## 8. Iniciar

Windows: `.\iniciar.ps1` · Linux: `./iniciar.sh`

Abra **http://127.0.0.1:8200** no navegador e entre com o login `admin`.

**Confirme que funcionou:**

1. http://127.0.0.1:8200/api/health mostra `{"status":"ok"...}`.
2. Depois de entrar, o menu à esquerda aparece e o *Painel* mostra os cartões.
3. Cadastre um órgão em *Órgãos*: ele aparece na lista na hora.

## 9. Rodar os testes

Os testes usam um banco **de teste** separado (ele é apagado a cada execução). Crie-o como no passo 2 do manual do banco, com o nome `digitalgov_gerenciador_teste`, e rode:

```bash
cd backend
TEST_DATABASE_URL="postgresql+psycopg://gerenciador_app:SENHA@127.0.0.1:5432/digitalgov_gerenciador_teste" python -m pytest -q
```

No Windows: `$env:TEST_DATABASE_URL="postgresql+psycopg://gerenciador_app:SENHA@127.0.0.1:5432/digitalgov_gerenciador_teste"; python -m pytest -q`
