# Tutorial: criar um projeto e ligá-lo ao gerenciador

Exemplo real usado neste tutorial: o projeto `proj-protocolo`, que está em `projetos/proj-protocolo`.

## 1. Criar o projeto com banco próprio (um comando)

Pré-requisitos: gerenciador instalado (`MANUAL_INSTALACAO.md`) e `PG_ADMIN_URL` no `.env` do gerenciador (`MANUAL_BANCO_DE_DADOS.md`, passo 3).

Linux (pasta `digitalgov-gerenciador`):

```bash
set -a && . ./.env && set +a
cd backend
python -m app.cli projeto criar --codigo proj-protocolo --nome "Protocolo Digital" --porta 8100 --criar-banco --registrar
```

Windows (PowerShell, pasta `digitalgov-gerenciador`):

```powershell
Get-Content .env | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object { $n,$v = $_ -split '=',2; Set-Item "env:$n" $v }
cd backend
python -m app.cli projeto criar --codigo proj-protocolo --nome "Protocolo Digital" --porta 8100 --criar-banco --registrar
```

O comando faz, nesta ordem:

1. cria o usuário `proj_protocolo_app` e os bancos `proj_protocolo` e `proj_protocolo_teste`, fechados para outros usuários;
2. copia o modelo para `projetos/proj-protocolo` (back-end, front-end, migrações, testes, backup, Docker, README);
3. grava a conexão e um token no `.env` do projeto **e** no `.env` do gerenciador (`PROJ_PROTOCOLO_DATABASE_URL` e `PROJ_PROTOCOLO_TOKEN`). A senha não aparece na tela;
4. registra o projeto no gerenciador.

**Confirme:** `PROJ_PROTOCOLO_DATABASE_URL` está no `.env` do gerenciador e o projeto aparece em *Projetos e START*.

Sem `--criar-banco`, o comando só copia o modelo; aí crie o banco à mão (manual do banco, passo 2, trocando os nomes) e preencha o `.env` do projeto a partir do `.env.example`.

## 2. Criar as tabelas do projeto e rodar os testes

Linux:

```bash
cd ../../proj-protocolo
python3 -m venv .venv && . .venv/bin/activate      # ou use o mesmo .venv do gerenciador
pip install -r backend/requirements-dev.txt
set -a && . ./.env && set +a
cd backend
alembic upgrade head
python -m pytest -q --junitxml=../junit.xml
```

Windows: os mesmos passos, carregando o `.env` com a linha `Get-Content .env | ...` mostrada acima e usando `.\.venv\Scripts\Activate.ps1`.

**Confirme:** `alembic current` mostra `0001 (head)` e o pytest termina com `4 passed`.

## 3. Ligar o back-end, o front-end e o banco

Ainda em `proj-protocolo/backend`:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8100
```

O front-end (`frontend/`) é servido pelo próprio back-end, no mesmo endereço; por isso as telas chamam a API como `/api/...`, sem configurar endereço. Se um dia o front-end ficar em outro servidor, ele deve apontar para o endereço do back-end e o back-end precisa liberar esse endereço (CORS).

Abra http://127.0.0.1:8100. A linha de cima mostra "banco ok, migração 0001": isso prova que tela → API → banco estão ligados.

## 4. Conferir que os registros são gravados

1. Na tela do projeto, preencha *Título do registro* e clique em **Gravar**. Ele aparece em *Registros gravados*.
2. Confira no banco: `psql "postgresql://proj_protocolo_app:SENHA@127.0.0.1:5432/proj_protocolo" -c "SELECT id, titulo FROM registros;"` (a senha está no `.env` do projeto).

## 5. Conectar ao gerenciador

Se usou `--registrar`, a ligação já existe. Para um projeto antigo, em *Projetos e START → Cadastrar projeto existente* preencha:

| Campo | Exemplo |
|---|---|
| Código | `proj-protocolo` |
| Pasta | `proj-protocolo` (relativa à pasta de projetos) |
| Endereço do repositório | link do GitHub |
| Endereço do serviço | `http://127.0.0.1:8100` |
| Variável do banco | `PROJ_PROTOCOLO_DATABASE_URL` |
| Variável do token | `PROJ_PROTOCOLO_TOKEN` |

As duas variáveis precisam estar no `.env` do gerenciador, e o token tem de ser igual ao `GERENCIADOR_TOKEN` do `.env` do projeto. Depois de alterar o `.env`, reinicie o gerenciador.

Vincule o projeto a um contrato e a uma ordem de serviço **autorizada** (cadastros *Contratos* e *Ordens de serviço*), pelo cadastro do projeto.

**Confirme no painel (*Projetos e START*):**

- Banco de dados: OK, "Conectado ao banco proj_protocolo, migração 0001";
- Serviço: OK;
- Código: OK, com a mensagem do último commit;
- Agentes: "Integração pendente".

## 6. Botão START

Clique em **START**. O gerenciador confere: projeto ativo → contrato vigente → OS autorizada → banco → serviço. Se tudo estiver certo, ele chama o projeto, que registra um ciclo de produção no próprio banco (tabela `ciclos_producao`). Os agentes continuam "Integração pendente" até existir um conector instalado; nada é simulado.

## 7. Testes e evidências no painel

- *Testes* → escolha o projeto → envie o `junit.xml` gerado no passo 2. O painel mostra total, falhas e ignorados.
- *Evidências* → registre commits, capturas e logs de cada tarefa.

## 8. Backup do projeto

```bash
cd projetos/proj-protocolo
./infra/scripts/backup.sh /srv/backups/proj-protocolo
./infra/scripts/restore.sh /srv/backups/proj-protocolo/proj-protocolo-AAAAMMDDTHHMMSS.dump   # pare o projeto antes
```
