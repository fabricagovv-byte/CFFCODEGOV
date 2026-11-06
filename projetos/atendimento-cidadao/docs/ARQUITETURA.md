# Arquitetura — Gestão Documental Pública

## Visão geral

```
Navegador ──HTTPS──> [proxy Nginx TLS] ──> [frontend Nginx: SPA + /api] ──> [backend FastAPI] ──> [PostgreSQL]
                                                                               └──> volume de arquivos PDF
```

- **Frontend** (React/TS): SPA; token JWT em `sessionStorage` (some ao fechar a aba); toda autorização é revalidada no servidor.
- **Backend** (FastAPI): rotas em `app/routers/` (uma por módulo), regras de acesso em `app/permissions.py`, auditoria em `app/audit.py`, armazenamento em `app/storage.py`.
- **Banco**: PostgreSQL 16, migrações Alembic (`backend/migrations`). `alembic check` confirma que o modelo e as migrações estão sincronizados.
- **Arquivos**: fora do banco, em volume (`/dados/uploads/AAAA/MM/<uuid>.pdf`), com SHA-256 registrado.

## Modelo de dados

| Tabela | Finalidade | Observações |
|---|---|---|
| usuarios | contas e perfis | e-mail único; senha com bcrypt |
| tokens_recuperacao | redefinição de senha | guarda só o hash do token; 30 min; uso único |
| tokens_revogados | logout | jti do JWT até expirar |
| documentos | cadastro documental | número `AAAA/NNNNNN`; classificação PUBLICO/RESTRITO/SIGILOSO |
| arquivos | PDFs anexados | FK para documento; hash e tamanho |
| auditoria | trilha | somente inserção; trigger bloqueia UPDATE/DELETE |

## Perfis

| Perfil | Pode |
|---|---|
| ADMIN | tudo, inclusive gerenciar usuários |
| GESTOR | documentos (todas as classificações), arquivar, painel, auditoria |
| OPERADOR | criar/editar documentos públicos e restritos, enviar PDF |
| CONSULTA | ler e baixar documentos públicos |

## Decisões (ADR resumidas)

1. **FastAPI + PostgreSQL**: stack aberta, sem licença, comum em órgãos públicos; troca por Java/.NET possível se o TR exigir.
2. **JWT com revogação por jti**: permite logout real sem sessão no servidor.
3. **Exclusão lógica (ARQUIVADO)**: documentos públicos não são apagados (gestão documental e LAI).
4. **Auditoria imutável no banco**: garante a trilha mesmo contra erro da aplicação.
5. **404 para documento não visível**: não revela a existência de documento restrito.

## Requisitos não funcionais

- Paginação em todas as listagens (máx. 100/200 itens por página).
- Limite de upload configurável (`MAX_UPLOAD_MB`), validação da assinatura `%PDF-`.
- Pool de conexões (10 + 20) e `pool_pre_ping`.
- Capacidade estimada: um backend com 2–4 workers atende dezenas de usuários simultâneos; escalar horizontalmente exige mover o limitador de login para Redis.
- Acessibilidade: rótulos em todos os campos, foco visível, link "pular para o conteúdo", mensagens com `role=alert`, tema claro/escuro.
