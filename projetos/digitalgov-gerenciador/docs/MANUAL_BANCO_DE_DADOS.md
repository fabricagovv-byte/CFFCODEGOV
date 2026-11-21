# Manual de banco de dados

Cada sistema tem o **seu próprio banco e o seu próprio usuário**. O gerenciador usa o banco `digitalgov_gerenciador`; cada projeto usa um banco com o nome do projeto. Um usuário de projeto não consegue entrar no banco do gerenciador nem no de outro projeto.

## 1. Como entrar no PostgreSQL como administrador

- **Windows:** abra o PowerShell e rode `psql -U postgres -h 127.0.0.1`. Ele pede a senha do superusuário criada na instalação.
  - Pelo **pgAdmin** (menu Iniciar → pgAdmin 4): clique em *Servers* → *PostgreSQL 16*, digite a senha, depois clique com o botão direito em *PostgreSQL 16* → *Query Tool*. Os comandos SQL abaixo podem ser colados ali e executados com o botão ▶.
- **Linux:** `sudo -u postgres psql`

Você está no lugar certo quando aparece o sinal `postgres=#`.

## 2. Criar o banco central do gerenciador

Primeiro gere uma senha forte (copie o resultado para o gerenciador de senhas):

- Windows: `python -c "import secrets; print(secrets.token_urlsafe(24))"`
- Linux: `python3 -c "import secrets; print(secrets.token_urlsafe(24))"`

No `psql` (ou na Query Tool do pgAdmin), troque `SENHA_GERADA` pela senha e execute:

```sql
CREATE ROLE gerenciador_app LOGIN PASSWORD 'SENHA_GERADA';
CREATE DATABASE digitalgov_gerenciador OWNER gerenciador_app;
REVOKE CONNECT ON DATABASE digitalgov_gerenciador FROM PUBLIC;
-- banco de testes (é apagado pelos testes)
CREATE DATABASE digitalgov_gerenciador_teste OWNER gerenciador_app;
REVOKE CONNECT ON DATABASE digitalgov_gerenciador_teste FROM PUBLIC;
```

Saia com `\q`.

**Confirme:** `psql "postgresql://gerenciador_app:SENHA_GERADA@127.0.0.1:5432/digitalgov_gerenciador" -c "select current_user, current_database();"` deve mostrar `gerenciador_app | digitalgov_gerenciador`.

## 3. Usuário que cria bancos de projetos (para o comando `projeto criar`)

Para o gerenciador criar sozinho o banco de cada projeto novo, crie um usuário com permissão de criar bancos (não é o superusuário):

```sql
CREATE ROLE dg_criador LOGIN CREATEDB CREATEROLE PASSWORD 'OUTRA_SENHA_GERADA';
```

E acrescente ao `.env` do gerenciador:

```
PG_ADMIN_URL=postgresql+psycopg://dg_criador:OUTRA_SENHA_GERADA@127.0.0.1:5432/postgres
```

## 4. Credenciais com segurança

| Faça | Não faça |
|---|---|
| Guarde as senhas no `.env` (fora do GitHub) e num gerenciador de senhas | Não escreva senha em código, relatório, planilha ou mensagem |
| No Linux: `chmod 600 .env` | Não use o superusuário `postgres` no sistema |
| Uma senha diferente por banco | Não reutilize a senha de um projeto em outro |
| No cadastro do projeto, informe só o **nome da variável** (ex.: `PROJ_PROTOCOLO_DATABASE_URL`) | Não digite a conexão com senha no painel (ele recusa) |

Formato da conexão (variável de ambiente):

```
postgresql+psycopg://USUARIO:SENHA@SERVIDOR:5432/BANCO
```

Se a senha tiver caracteres especiais (`@ : / ? # %`), use as senhas geradas pelo comando do passo 2, que só têm letras, números, `-` e `_`.

## 5. Ligar o back-end ao banco

O back-end lê a conexão da variável `GERENCIADOR_DATABASE_URL` (gerenciador) ou `DATABASE_URL` (projetos), definida no `.env`. Os scripts `iniciar.sh` / `iniciar.ps1` carregam o `.env` antes de subir.

**Confirme:** com o sistema no ar, http://127.0.0.1:8200/api/health responde `ok` (gerenciador) e http://127.0.0.1:PORTA/health do projeto mostra `"migracao": "0001"`.

## 6. Migrações

Dentro da pasta `backend` (com o `.env` carregado):

| Comando | O que faz |
|---|---|
| `alembic upgrade head` | Cria ou atualiza as tabelas até a última versão |
| `alembic current` | Mostra a versão atual do banco |
| `alembic history` | Lista todas as versões |
| `alembic downgrade -1` | Volta uma versão (use só seguindo o tutorial de implantação) |
| `alembic check` | Confere se o banco bate com o código |

## 7. Conferir se os registros estão sendo gravados

Exemplo no banco do projeto de exemplo, depois de gravar um registro pela tela do projeto:

```bash
psql "postgresql://proj_protocolo_app:SENHA@127.0.0.1:5432/proj_protocolo" -c "SELECT id, titulo, criado_em FROM registros ORDER BY id DESC LIMIT 5;"
```

No banco do gerenciador, as horas lançadas:

```bash
psql "postgresql://gerenciador_app:SENHA@127.0.0.1:5432/digitalgov_gerenciador" -c "SELECT id, data, inicio, fim, atividade FROM lancamentos_horas ORDER BY id DESC LIMIT 5;"
```

No **pgAdmin**: *Servers → PostgreSQL 16 → Databases → nome do banco → Schemas → public → Tables*, clique com o botão direito na tabela → *View/Edit Data → Last 100 Rows*.

## 8. Backup e restauração

**Linux** (dentro da pasta do gerenciador):

```bash
./infra/scripts/backup.sh /srv/backups                        # gera gerenciador-AAAAMMDDTHHMMSS.dump + documentos + SHA-256
./infra/scripts/restore.sh /srv/backups 20261106T180000       # pare o gerenciador antes
```

**Windows** (PowerShell, com o `.env` carregado):

```powershell
$url = $env:GERENCIADOR_DATABASE_URL -replace '\+psycopg',''
$carimbo = Get-Date -Format "yyyyMMddTHHmmss"
pg_dump --format=custom --no-owner --file "C:\backups\gerenciador-$carimbo.dump" $url
Get-FileHash "C:\backups\gerenciador-$carimbo.dump" -Algorithm SHA256 | Out-File "C:\backups\gerenciador-$carimbo.sha256"
# restaurar (pare o gerenciador antes):
pg_restore --clean --if-exists --no-owner --single-transaction --dbname $url "C:\backups\gerenciador-$carimbo.dump"
```

Cada projeto tem os mesmos scripts em `infra/scripts/` (backup do banco do próprio projeto).

**Confirme:** faça um backup, cadastre um órgão de teste, restaure o backup e veja que o órgão de teste sumiu da lista. Repita esse teste uma vez por mês.
