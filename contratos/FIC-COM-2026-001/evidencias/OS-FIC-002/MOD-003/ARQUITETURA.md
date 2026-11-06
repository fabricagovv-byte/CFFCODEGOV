# Arquitetura — MOD-003 MOD-003 Base técnica — migrações versionadas, cabeçalhos de segurança, dependências

- `app/migrations.py`: lê os arquivos SQL, aplica cada migração numa transação com chaves estrangeiras desligadas, confere `foreign_key_check` e só então grava em `schema_migrations`.
- `app/db.py`: `init()` passou a chamar as migrações.
- Middleware HTTP acrescenta os cabeçalhos; `/docs` fica sem CSP porque a documentação interativa usa recursos externos.
