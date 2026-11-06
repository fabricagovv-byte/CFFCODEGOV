# Manual de publicação

Publicar em homologação ou produção exige autorização registrada do responsável (quem, quando e documento).

## 1. Pré-requisitos

- Servidor Linux com Docker e Docker Compose.
- Domínio apontando para o servidor e certificado TLS (`fullchain.pem` e `privkey.pem`) fornecido pelo órgão ou emitido por autoridade certificadora.
- Arquivo `.env` preenchido a partir de `.env.example` (`DG_COMM_SECRET`, `DG_FACTORY_TOKEN`, `DOMINIO`, `CERTS_DIR`). O `.env` nunca vai para o repositório.

## 2. Publicar

```bash
git fetch --tags && git checkout <versão>                 # ex.: v1.1.0
infra/scripts/backup.sh /srv/backups                       # sempre antes de publicar (ver item 4)
docker compose -f docker-compose.yml -f docker-compose.prod.yml config -q
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose ps                                          # todos "healthy"
curl -fsS https://$DOMINIO/health
```

O contêiner da plataforma aplica as migrações pendentes ao iniciar (`python -m app.cli init`).

## 3. Conferir depois de publicar

1. `https://<domínio>/health` responde `{"status": "ok"}`.
2. Login com um usuário de teste, abrir Publicações e Atendimento.
3. `docker compose logs --since 10m comunicacao` sem erros.

## 4. Voltar à versão anterior (rollback)

Use quando a conferência do item 3 falhar.

```bash
docker compose exec -T comunicacao python -m app.cli migrations     # versão atual do banco
docker compose stop comunicacao
# se a versão nova criou migrações, desfaça-as AINDA com a imagem nova (ela tem os arquivos .down.sql):
docker compose run --rm comunicacao python -m app.cli rollback --to <versão do banco da anterior>
git checkout <versão anterior>
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Se o banco foi danificado, restaure o backup feito no item 2 (veja `docs/MANUAL_OPERACAO.md`, Restauração).

Cada migração tem o caminho de volta em `PLATAFORMA_COMUNICACAO/migrations/NNNN_nome.down.sql`.

## 5. Segurança

- O painel da fábrica fica preso a `127.0.0.1:8777` e não deve ser publicado.
- Só o Nginx (portas 80 e 443) fica exposto; HTTP redireciona para HTTPS; HSTS ativo.
- Limite de tentativas de login no Nginx e na aplicação.
