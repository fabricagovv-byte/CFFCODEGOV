# Plano de continuidade e recuperação de desastres

## Objetivos (a confirmar com o órgão)

- RPO (perda máxima de dados): 24 h com backup diário; reduzir com backups mais frequentes ou replicação.
- RTO (tempo para voltar): 4 h.

## Cenários

| Cenário | Resposta |
|---|---|
| Falha do contêiner | `restart: unless-stopped`; verificar `docker compose ps` e logs |
| Corrupção/erro no banco | `infra/scripts/restore.sh <último CARIMBO íntegro>` |
| Perda do servidor | novo servidor → seções 1 e 3 do manual de publicação → restaurar último backup externo |
| Vazamento de credencial | trocar `JWT_SECRET` (encerra todas as sessões) e senhas do banco; registrar incidente; avaliar comunicação à ANPD (LGPD art. 48) |
| Versão com defeito | rollback (manual de publicação, seção 5) |

## Backups

- Banco (`pg_dump -Fc`) + PDFs (`tar.gz`) + arquivo `.sha256` de conferência.
- Guardar cópia fora do servidor (storage do órgão), com acesso restrito.
- Testar restauração mensalmente e registrar o resultado como evidência.

## Transição ao fim do contrato

Entregar: código-fonte, migrações, imagens/Dockerfiles, `.env.example`, último backup validado, manuais e o histórico de commits.
