# Gerenciador Central DigitalGov

Painel da fábrica para controlar contratos, órgãos, ordens de serviço, projetos, profissionais, agentes, horas, medições, testes, evidências e relatórios. Cada projeto tem pasta, código, banco de dados e migrações próprios; o gerenciador guarda só os dados administrativos no seu banco central.

| Parte | Onde está |
|---|---|
| Banco central (PostgreSQL) | `backend/migrations/` (Alembic) e `backend/app/modelos.py` |
| Back-end (API FastAPI) | `backend/app/` — rotas em `backend/app/rotas/`, regras em `backend/app/servicos/` |
| Front-end (painel) | `frontend/` |
| Testes | `backend/tests/` (rodam no PostgreSQL) |
| Linha de comando | `backend/app/cli.py` (administrador, importações, criação de projetos) |
| Modelo de projeto | `modelo_projeto/` (usado por `projeto criar`) |
| Backup | `infra/scripts/backup.sh` e `restore.sh` |
| Implantação | `Dockerfile`, `docker-compose.yml` |

## Primeiro administrador

Com o banco vazio, crie o administrador (a senha é digitada sem eco; mínimo de 12 caracteres, com letras e números):

```bash
cd backend
python3 -m app.bootstrap --login admin --nome "Administrador"
```

Os demais usuários são criados pelo administrador na tela Usuários.

## Testes

```bash
cd backend
TEST_DATABASE_URL=postgresql+psycopg://usuario:senha@127.0.0.1:5432/banco_de_teste python3 -m pytest -q
```

O banco de teste é apagado a cada teste: nunca aponte para o banco real.

## Manuais

1. `docs/MANUAL_INSTALACAO.md` — instalar as ferramentas e o gerenciador (Windows e Linux)
2. `docs/MANUAL_BANCO_DE_DADOS.md` — criar bancos, credenciais, migrações, conferir registros, backup e restauração
3. `docs/TUTORIAL_NOVO_PROJETO.md` — criar um projeto com banco próprio e ligá-lo ao gerenciador
4. `docs/TUTORIAL_IMPLANTACAO.md` — publicar em servidor e atualizar sem perder dados

## O que o gerenciador não faz

- Não executa agentes: enquanto não houver conector instalado, o START mostra "Integração pendente".
- Não altera horas lançadas, não aceita medições sozinho e não cria funcionalidades de contrato: ele controla e mede o que existe.
- Não guarda senhas de banco: cada projeto aponta para uma variável de ambiente.
