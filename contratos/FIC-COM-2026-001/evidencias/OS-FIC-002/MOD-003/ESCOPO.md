# Escopo — MOD-003 Base técnica — migrações versionadas, cabeçalhos de segurança, dependências

- Contrato: FIC-COM-2026-001 · OS: OS-FIC-002
- Item contratual: CORRETIVA-SEM-ITEM · Previsto: 0

## Descrição
Base técnica pedida no TR (seção 6: migrações em banco vazio e plano de reversão; RNF-06 segurança) e achados 8, 9 e 13. Não é item de escopo dos 18 módulos; não é medido.

## Funcionalidades
- Migrações versionadas em `migrations/NNNN_nome.up.sql` com `.down.sql` de reversão; tabela `schema_migrations`.
- Banco criado pela versão original do pacote é reconhecido como versão 1, sem perder dados.
- Comandos `init`, `migrations` e `rollback --to N` na linha de comando.
- Cabeçalhos CSP, X-Frame-Options, X-Content-Type-Options e Referrer-Policy; API sem cache.
- Dependências com versão fixa: `requirements.txt` (produção) e `requirements-dev.txt` (testes).
- Implantação: Dockerfile da plataforma e do painel, `docker-compose.yml` (Nginx + plataforma + painel só local) e `docker-compose.prod.yml` (Nginx com TLS e HSTS); arquivos validados com `docker compose config`.
- Backup e restauração dos bancos (`infra/scripts/backup.sh` e `restore.sh`) com SHA-256, verificação de integridade e retenção; 2 testes automáticos.
- Manuais: `README.md`, `docs/MANUAL_PUBLICACAO.md` (publicação e volta à versão anterior), `docs/MANUAL_OPERACAO.md`, `docs/PLANO_CONTINUIDADE.md`.
- Integração contínua: etapa `comunicacao` em `.github/workflows/ci.yml` (testes, migrações ida e volta, Compose e construção das imagens).

## Fora do escopo
- Troca do SQLite por PostgreSQL (aguarda decisão do responsável).
- Construção das imagens Docker neste ambiente (o serviço Docker não está disponível aqui; a construção roda na CI).
- Monitoramento com alertas e métricas (M18).

Linha de base: o commit `f823f56` é a importação do código original do pacote DIGITALGOV (aparece no git porque os arquivos nasceram nele); não é trabalho desta OS e não é medido.
