# Escopo — MOD-007 Infraestrutura e documentação

- Contrato: TESTE-001 (fictício) · OS: OS-TESTE-001

## Descrição
Base da API (configuração, banco, modelo, esquemas), migrações Alembic, Dockerfiles, Docker Compose (dev/homologação e sobreposição de produção com TLS), Nginx, backup/restauração, CI e documentação.

## Funcionalidades
- docker-compose.yml / docker-compose.prod.yml
- backend/Dockerfile, frontend/Dockerfile, nginx
- infra/scripts: backup.sh, restore.sh, verificar_ambiente.sh
- docs/: arquitetura, publicação, operação, continuidade, segurança, preview

## Fora do escopo
- Provisionamento do servidor do órgão
- Monitoramento externo
