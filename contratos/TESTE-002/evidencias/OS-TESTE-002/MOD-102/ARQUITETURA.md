# Arquitetura — MOD-102 Cadastro de protocolos

Tabela `protocolos`:

| Campo | Tipo | Obrigatório | Único | Dado pessoal |
|---|---|---|---|---|
| numero | texto | sim | sim |  |
| assunto | texto | sim |  |  |
| interessado_id | referencia | sim |  |  |
| canal | enum | sim |  |  |
| prioridade | enum | sim |  |  |
| prazo | data | não |  |  |
| valor_taxa | decimal | não |  |  |
| quantidade_folhas | inteiro | não |  |  |
| sigiloso | booleano | não |  |  |

Arquivos: `backend/app/modulos/protocolos/` (models, schemas, router), migração Alembic, `frontend/src/modulos/protocolos/` (api.ts, página, teste). Exclusão lógica (`ativo`).
