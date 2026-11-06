# Arquitetura — MOD-002 MOD-002 Correções de validação e privacidade (M03, M05, M07, M08)

- Regras por perfil aplicadas no servidor (consulta SQL filtrada para VIEWER).
- Migração 0003 recria a tabela `campaigns` com chave estrangeira para `channels` (SQLite não altera FK em tabela existente); a migração confere `PRAGMA foreign_key_check` e não grava nada se houver referência quebrada.
- `celula_segura()` prefixa com apóstrofo as células de texto perigosas no CSV.
