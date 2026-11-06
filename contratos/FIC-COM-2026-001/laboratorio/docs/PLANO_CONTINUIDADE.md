# Plano de continuidade e recuperação de desastres

Valores de RPO e RTO abaixo são proposta da contratada e precisam ser pactuados com o órgão.

| Indicador | Proposta |
|---|---|
| RPO (perda máxima de dados) | 24 horas (backup diário) |
| RTO (tempo para voltar a funcionar) | 4 horas |
| Retenção de backups | 14 cópias diárias |

## Cenários

| Cenário | Ação |
|---|---|
| Falha da aplicação após publicação | Rollback (docs/MANUAL_PUBLICACAO.md, item 4) |
| Banco corrompido | Restaurar o último backup (docs/MANUAL_OPERACAO.md, Restauração) |
| Perda do servidor | Novo servidor com Docker, código da versão publicada, `.env` guardado em cofre, restauração do último backup |
| Vazamento de segredo | Trocar `DG_COMM_SECRET` (encerra todas as sessões) e `DG_FACTORY_TOKEN`, publicar, registrar o incidente |
| Incidente com dados pessoais | Conter, registrar, comunicar o encarregado do órgão e seguir a LGPD |

## Onde ficam as cópias

- Backups: pasta fora do servidor da aplicação (outro servidor ou armazenamento do órgão), com acesso restrito.
- Segredos (`.env`): cofre de senhas do órgão ou da contratada, nunca no repositório.

## Teste do plano

Uma vez por mês: restaurar o último backup num ambiente de teste, subir a aplicação e conferir login, publicações e chamados. Registrar data, responsável e resultado.
