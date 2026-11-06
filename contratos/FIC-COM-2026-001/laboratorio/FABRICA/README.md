# Digitalgov Factory Control Center — núcleo funcional

Controle de contrato fictício, OS, projetos, tarefas, 10 pessoas (7 nomes informados + 3 vagas), tempos comprovados, UST previstas/verificadas/homologadas e audit trail em SQLite.

```bash
cd FABRICA
pip install -r requirements.txt
python -m app.cli init
python -m app.cli seed-fiction
export DG_FACTORY_TOKEN=$(python -c 'import secrets;print(secrets.token_urlsafe(48))')  # chave do painel; guarde-a
uvicorn app.main:app --host 127.0.0.1 --port 8777
```

Acesse http://127.0.0.1:8777.

**Segurança:** desde a OS-FIC-002 (06/11/2026) toda a API do painel exige a chave `DG_FACTORY_TOKEN` (32+ caracteres, enviada como `Authorization: Bearer`); sem a variável a API fica fechada (HTTP 503). É uma chave única, sem perfis por pessoa. Execute SOMENTE em `127.0.0.1`; nunca exponha esse serviço à internet nem dados reais sem adicionar autenticação/RBAC, HTTPS, logs protegidos, segredos e autorizações. O botão START não chama 100 agentes Codex. Ele requer confirmação expressa e gera prompts por tarefa em `data/codex_inbox` para execução real via interface/CLI do Codex. O conector externo e a fila distribuída ainda não estão implementados. Não há emissão oficial de aceite.

## Testes
`pytest -q tests`

## Indicadores
- `ust_planned`: metas em tarefas em minuta — NÃO são executadas.
- `ust_verified`: aferição técnica por revisor com evidência SHA-256 e teste PASS.
- `ust_homologated`: somente após vínculo de referência documental externa; nesta versão o sistema **não verifica autenticidade** do documento externo, portanto não deve ser usado para faturamento governamental sem integração/validação humana.
- `hours`: apenas tempo efetivamente informado com evidência e proteção contra sobreposição; a ferramenta não prova a presença física do humano.
