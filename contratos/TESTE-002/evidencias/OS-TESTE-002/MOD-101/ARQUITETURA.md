# Arquitetura — MOD-101 Cadastro de interessados

Tabela `interessados`:

| Campo | Tipo | Obrigatório | Único | Dado pessoal |
|---|---|---|---|---|
| nome | texto | sim |  |  |
| documento | cpf_cnpj | sim | sim | sim |
| tipo_pessoa | enum | sim |  |  |
| email | email | não |  | sim |
| telefone | texto | não |  | sim |
| observacoes | texto_longo | não |  |  |

Arquivos: `backend/app/modulos/interessados/` (models, schemas, router), migração Alembic, `frontend/src/modulos/interessados/` (api.ts, página, teste). Exclusão lógica (`ativo`).
