---
name: importar-planilha
description: IMPORTAR PLANILHA / IMPORTAR DOCUMENTO BASE — importa o DOCUMENTO_BASE.xlsx (ou CSVs) enviada pelo usuário para o contrato - dados do contrato, equipe com CPF protegido, participações, totais para rateio, tabela UST, produção histórica e lista de projetos.
---
# IMPORTAR PLANILHA (G18 Gestor de Profissionais, G02, G03)

1. Salve o arquivo recebido fora de pastas versionadas sensíveis (ex.: `contratos/<ID>/documentos/` se não tiver CPF; se tiver CPF, em `contratos/<ID>/privado/`).
2. `python3 fabrica/ferramentas/fabrica.py planilha importar <ID> <arquivo.xlsx>` (cria o contrato se não existir).
3. Mostre ao usuário: quantos profissionais (novos/total), erros (CPF inválido, senioridade inválida), linhas por aba. **Nunca mostre CPF completo** — só o mascarado.
4. `python3 fabrica/ferramentas/fabrica.py contrato faltantes <ID>` e pergunte só o que faltar.
5. Se a aba PROJETOS tiver linhas, ofereça criar os repositórios (skill novo-repositorio).
6. Se precisar da lista oficial com CPF para o órgão: `python3 fabrica/ferramentas/fabrica.py profissionais oficial <ID>` (gera em privado/, não versionado).
