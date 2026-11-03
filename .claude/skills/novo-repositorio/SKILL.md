---
name: novo-repositorio
description: NOVO REPOSITÓRIO / NOVO SISTEMA — cria um repositório por sistema a partir do modelo da fábrica, com esqueleto na(s) linguagem(ns) escolhida(s), PROJETO.yaml, CI e contrato; em lote para muitos projetos (ex.- 30). Também cria perfil de stack para linguagem nova.
---
# NOVO REPOSITÓRIO (G01, G05 Arquiteto, G11 DevOps)

1. Escolha as stacks: `python3 fabrica/ferramentas/fabrica.py stacks listar` e veja `fabrica/stacks/VERIFICACAO.md`. Stack exigida pelo contrato prevalece.
2. Um sistema: `python3 fabrica/ferramentas/fabrica.py repositorio novo <pasta> --id <ORGAO-NNN-SIGLA> --sistema "<nome>" --orgao "<órgão>" --contrato <ID> --componente backend=<stack> --componente frontend=<stack>`.
3. Vários: aba PROJETOS da planilha (coluna componentes no formato `backend=java-spring;frontend=react-vite`) → `python3 fabrica/ferramentas/fabrica.py repositorio lote <planilha.xlsx> <pasta-base>`.
4. Em cada repositório criado: `python3 fabrica/ferramentas/fabrica.py projeto verificar --instalar` e informe o resultado real.
5. Publicar no GitHub exige o usuário criar o repositório remoto (ou autorizar). Instrua: criar repositório privado vazio → `git remote add origin <url> && git add -A && git commit -m "fabrica: repositório inicial" && git push -u origin main`.
6. Linguagem sem perfil: crie `fabrica/stacks/<id>.yaml` + pasta com esqueleto (endpoint /api/health, um teste, Dockerfile) e rode `python3 fabrica/ferramentas/fabrica.py stacks verificar <id>`.
