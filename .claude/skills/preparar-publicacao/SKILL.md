---
name: preparar-publicacao
description: PREPARAR PUBLICAÇÃO — gera/atualiza o plano de implantação (homologação e produção), checa pré-requisitos, backup e rollback, sem publicar.
---
# PREPARAR PUBLICAÇÃO (G11, G10, G20)

1. Revise `docs/MANUAL_PUBLICACAO.md` do projeto para o ambiente do órgão (servidor, domínio, certificados, SMTP, backup externo).
2. Confirme: `.env` de produção fora do git, `JWT_SECRET` forte, `APP_ENV=prod`, sem DEMO.
3. Valide localmente: `docker compose -f docker-compose.yml -f docker-compose.prod.yml config`.
4. Liste o que depende do órgão (DNS, TLS, firewall, SMTP) como bloqueio.
5. Não publique. Encaminhe para autorização humana.
