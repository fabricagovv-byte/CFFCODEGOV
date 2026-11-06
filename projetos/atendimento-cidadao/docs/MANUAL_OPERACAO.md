# Manual de operação e manutenção

## Rotina

| Atividade | Comando | Frequência |
|---|---|---|
| Ver estado | `docker compose ps` | diária |
| Logs da API | `docker compose logs --since 24h backend` | diária |
| Saúde | `curl -fsS https://DOMINIO/api/health/db` | monitoramento a cada 1 min |
| Backup | `infra/scripts/backup.sh /caminho/backups` (cron 02:00; `BACKUP_GPG_DESTINATARIO` para criptografar) | diária |
| Proteger `.env` | `chmod 600 .env` | na instalação |
| Teste de restauração | `infra/scripts/restore.sh CARIMBO` em ambiente de homologação | mensal |
| Atualizar imagens base | `docker compose build --pull` | mensal / alerta de segurança |

Exemplo de cron: `0 2 * * * cd /opt/gestao-documental && infra/scripts/backup.sh /backups >> /var/log/gd-backup.log 2>&1`

## Monitoramento

- Cada requisição gera log com `rid` (X-Request-ID), método, rota, status e tempo.
- Alertas sugeridos: `/api/health/db` falhando, taxa de HTTP 5xx > 1%, disco > 80%, falhas de backup.
- Os logs em JSON do Docker podem ser coletados por Loki/ELK/Graylog do órgão.

## Usuários

- Criar/desativar usuários: Painel → Usuários (perfil ADMIN).
- Usuário bloqueado por tentativas: aguarda `LOGIN_BLOQUEIO_MIN` minutos (padrão 15).

## Manutenção do banco

- `docker compose exec db psql -U gd_app -d gestao_documental`
- Limpeza de tokens expirados: `DELETE FROM tokens_revogados WHERE expira_em < now(); DELETE FROM tokens_recuperacao WHERE expira_em < now();`
- A tabela `auditoria` não aceita UPDATE/DELETE (por desenho). Expurgo, se previsto em política, exige procedimento formal com DBA desabilitando o trigger e registro em ata.
