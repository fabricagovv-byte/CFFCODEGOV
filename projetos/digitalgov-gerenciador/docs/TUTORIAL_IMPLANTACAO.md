# Tutorial de implantação em servidor

Servidor recomendado: Linux Ubuntu 24.04 com Docker. Publicar em produção exige autorização registrada do responsável.

## 1. Preparar o servidor (uma vez)

Acesse o servidor por SSH (no Windows: PowerShell → `ssh usuario@IP_DO_SERVIDOR`).

```bash
sudo apt update && sudo apt install -y git nginx certbot python3-certbot-nginx postgresql-client
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER      # saia e entre de novo no SSH
docker --version && docker compose version
```

## 2. Baixar e configurar

```bash
sudo mkdir -p /srv/digitalgov && sudo chown $USER /srv/digitalgov && cd /srv/digitalgov
git clone https://github.com/fabricagovv-byte/cffcodegov.git
cd cffcodegov/projetos/digitalgov-gerenciador
cp .env.example .env && chmod 600 .env && nano .env
```

No `.env` do servidor, preencha `SENHA_BANCO_CENTRAL` com uma senha gerada (`python3 -c "import secrets;print(secrets.token_urlsafe(24))"`). A linha `GERENCIADOR_DATABASE_URL` pode ficar como está: no Docker ela é montada a partir de `SENHA_BANCO_CENTRAL`.

## 3. Subir

```bash
docker compose up -d --build
docker compose ps                                  # os dois serviços "healthy"
curl -fsS http://127.0.0.1:8200/api/health
docker compose exec gerenciador python -m app.cli criar-admin --nome "Seu Nome" --login admin
```

O contêiner aplica as migrações sozinho ao iniciar.

## 4. Endereço com HTTPS (Nginx)

Aponte o domínio (ex.: `gerenciador.suaempresa.com.br`) para o IP do servidor. Crie `/etc/nginx/sites-available/gerenciador`:

```nginx
server {
  server_name gerenciador.suaempresa.com.br;
  client_max_body_size 30m;
  location / {
    proxy_pass http://127.0.0.1:8200;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/gerenciador /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d gerenciador.suaempresa.com.br     # emite o certificado e liga o HTTPS
```

**Confirme:** https://gerenciador.suaempresa.com.br/api/health responde `ok` com o cadeado do navegador.

## 5. Backup automático

```bash
crontab -e
# todo dia às 2h:
0 2 * * * cd /srv/digitalgov/cffcodegov/projetos/digitalgov-gerenciador && docker compose exec -T banco-central pg_dump -U gerenciador_app -Fc digitalgov_gerenciador > /srv/backups/gerenciador-$(date +\%Y\%m\%d).dump
```

Copie a pasta `/srv/backups` para fora do servidor (outro servidor ou armazenamento do órgão).

## 6. Atualizar sem perder dados

Os dados ficam nos volumes do Docker (`banco_central` e `documentos`); `git pull` e `docker compose up --build` **não** apagam esses volumes. Mesmo assim, sempre faça backup antes:

```bash
cd /srv/digitalgov/cffcodegov/projetos/digitalgov-gerenciador
docker compose exec -T banco-central pg_dump -U gerenciador_app -Fc digitalgov_gerenciador > /srv/backups/antes-da-atualizacao.dump
docker compose exec -T gerenciador alembic current        # anote a versão do banco
git pull
docker compose up -d --build                               # aplica as migrações novas ao subir
docker compose ps && curl -fsS http://127.0.0.1:8200/api/health
```

Nunca rode `docker compose down -v`: o `-v` apaga os volumes com os dados.

## 7. Voltar à versão anterior

```bash
docker compose exec -T gerenciador alembic downgrade <versão anotada>   # ainda com a versão nova
git checkout <versão anterior>
docker compose up -d --build
```

Se o banco foi danificado: `docker compose exec -T banco-central pg_restore --clean --if-exists -U gerenciador_app -d digitalgov_gerenciador < /srv/backups/antes-da-atualizacao.dump`

## 8. Projetos no servidor

Cada projeto tem o próprio `docker-compose.yml` com o próprio PostgreSQL. Para cada um: entre na pasta, crie o `.env` (com `SENHA_BANCO` e `GERENCIADOR_TOKEN`), rode `docker compose up -d --build`, e no `.env` do gerenciador acrescente `PROJ_X_DATABASE_URL` e `PROJ_X_TOKEN` apontando para ele. Reinicie o gerenciador com `docker compose up -d`.
