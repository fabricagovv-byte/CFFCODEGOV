# Manual de operação e manutenção

## Rotina

| Tarefa | Frequência | Como |
|---|---|---|
| Backup dos bancos | Diária | `infra/scripts/backup.sh /srv/backups` (agendar no cron) |
| Conferir saúde | Diária | `docker compose ps` e `curl -fsS https://<domínio>/health` |
| Revisar a auditoria | Semanal | Tela Auditoria (perfil ADMIN ou APPROVER) |
| Atualizar dependências | Mensal | Atualizar `requirements.txt`, rodar os testes, publicar |
| Teste de restauração | Mensal | Restaurar o último backup num ambiente de teste |

## Usuários

```bash
docker compose exec comunicacao python -m app.cli add-user --name "Nome" --username login --role EDITOR --password '...'
```

Perfis: ADMIN (tudo), EDITOR (cria conteúdo e chamados), APPROVER (aprova e publica, exporta), VIEWER (só consulta o que foi publicado).

## Backup no Docker

O banco fica no volume `dados_comunicacao`. Para copiar e fazer o backup no servidor:

```bash
docker compose cp comunicacao:/dados/comunicacao.db ./dados/comunicacao.db
DG_COMM_DB=./dados/comunicacao.db infra/scripts/backup.sh /srv/backups
```

O script grava `comunicacao-AAAAMMDDTHHMMSS.db`, a lista `backup-*.sha256` e mantém os 14 mais recentes (`BACKUP_RETENCAO`).

## Restauração

```bash
docker compose stop comunicacao
infra/scripts/restore.sh /srv/backups/comunicacao-<carimbo>.db ./dados/comunicacao.db
docker compose cp ./dados/comunicacao.db comunicacao:/dados/comunicacao.db
docker compose start comunicacao
```

O script confere o SHA-256 e a integridade do arquivo antes de restaurar; se não conferir, não restaura nada.

## Monitoramento

- Saúde: `/health` (usado pelo `HEALTHCHECK` dos contêineres).
- Logs: `docker compose logs -f comunicacao proxy`.
- Bloqueios de login aparecem na auditoria como `LOGIN_BLOQUEADO`.
