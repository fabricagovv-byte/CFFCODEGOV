# Manual de publicação — passo a passo

> Publicar em **produção exige autorização humana registrada** (`autorizacao_execucao.pode_publicar_producao: true` no `contrato.yaml` + registro em `fabrica/comunicacao/AGENT_DECISIONS.md`). Os agentes não publicam sozinhos.

## 1. Pré-requisitos do servidor

- Linux (Ubuntu 24.04 LTS ou equivalente homologado pelo órgão), 2 vCPU, 4 GB RAM, 40 GB de disco (mais o volume de PDFs).
- Docker Engine 24+ com o plugin Compose.
- DNS do domínio apontando para o servidor; portas 80 e 443 liberadas.
- Certificado TLS do órgão (ou Let's Encrypt) em `infra/certs/fullchain.pem` e `privkey.pem`.

## 2. Homologação

```bash
git clone <repositorio> && cd <repositorio>/projetos/gestao-documental
cp .env.example .env && nano .env          # APP_ENV=homologacao, senhas e JWT_SECRET novos
docker compose up -d --build
set -a; . ./.env; set +a
docker compose exec -e ADMIN_EMAIL -e ADMIN_SENHA backend python -m app.seed   # cria o admin
curl -fsS http://localhost:8080/api/health          # {"status":"ok",...}
```

Roteiro de homologação: login de cada perfil, criar documento, anexar PDF, pesquisar, painel, auditoria, recuperação de senha (depende de SMTP do órgão).

## 3. Produção (somente com autorização)

```bash
cp .env.example .env    # APP_ENV=prod, DOMINIO, CERTS_DIR, senhas exclusivas de produção
infra/scripts/backup.sh                                   # se já houver versão anterior
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
set -a; . ./.env; set +a; docker compose exec -e ADMIN_EMAIL -e ADMIN_SENHA backend python -m app.seed   # só na 1ª implantação, sem DEMO
curl -fsS https://$DOMINIO/api/health
```

## 4. Atualização de versão

1. `git fetch && git checkout <tag-da-versao>`
2. `infra/scripts/backup.sh`
3. `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build` (as migrações rodam ao iniciar o backend)
4. Verificar `/api/health` e `/api/health/db`, testar login.

## 5. Rollback

1. `git checkout <tag-anterior>`
2. Se a versão nova alterou o banco: `infra/scripts/restore.sh <CARIMBO-do-backup-pre-atualizacao>`
3. `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build`
4. Registrar o incidente e a decisão no quadro (`fabrica.py decisao`).

## 6. Pendências que dependem do órgão

- SMTP institucional para o e-mail de recuperação de senha (hoje simulado em log).
- Integração com login gov.br, se exigida pelo TR.
- Política de retenção e backup externo (fora do servidor).
