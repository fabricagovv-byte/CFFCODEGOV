# Pacote de preenchimento — leia primeiro

## O documento base

`DOCUMENTO_BASE.xlsx` é o **documento único** que você preenche uma vez e entrega junto com o edital.
A fábrica lê o edital, cruza com o documento base e responde: **o que já atende, o que precisa ajustar e o que falta**
(`CONFRONTAR EDITAL <ID>`). O mínimo é a aba PROFISSIONAIS com **nome e função** de cada pessoa.

## Só a equipe? Use o Word

`EQUIPE_NOME_CPF_CARGO.docx`: uma tabela com **Nome, CPF e Cargo**. Preencha e devolva dizendo "IMPORTAR EQUIPE <ID>".
O documento oficial da equipe (para o órgão) sai no mesmo formato, em Word, e fica guardado fora do repositório.

## Relatórios em Word

Todos os relatórios (diário, semanal, mensal, por profissional, fechamento do dia, PPJ, medição, confronto com o edital) são entregues também em **Word**, com capa, indicadores e tabelas.

## O jeito mais fácil (celular)

Abra **`DOCUMENTO_BASE.xlsx`** no Excel ou Google Planilhas, preencha as abas e me envie.

| Aba | O que pôr | Obrigatório |
|---|---|---|
| EMPRESA | razão social, CNPJ, responsável legal, preposto, contato | sim, para o confronto |
| CAPACIDADES | tecnologias dominadas, certificações e atestados da empresa, metodologias, infraestrutura | recomendado |
| CONTRATO | dados do contrato (só a coluna "valor") | o que souber |
| PROFISSIONAIS | **nome e função** (mínimo); CPF, área, senioridade, formação, anos de experiência, certificações | sim |
| PARTICIPACOES | o que cada pessoa fez e a prova (commit, PR, ata, e-mail, "registro do gestor") | para relatório por pessoa e rateio |
| RATEIO_TOTAIS | total de UST de cada semana/mês para dividir (ex.: semanal, 2026-11-02, 250) | para o rateio em UST |
| TABELA_UST | catálogo de serviços do TR | sim, para medir |
| PRODUCAO_HISTORICA | produção já aceita em meses anteriores | para médias por profissional |
| PROJETOS | um sistema por linha (até 30 ou mais) | para criar os repositórios |
| PERFIS | perfis do órgão: valor/hora e fator UST (como no edital) | se o edital mede por hora/perfil |
| CATALOGO_SERVICOS | horas de cada perfil por serviço | idem |
| PLANEJAMENTO | **seu plano**: projeto, módulo, serviço, quantidade, início, fim, responsável | sim, para planejar |

## Sobre CPF e assinaturas

- **CPF:** usado só para a lista oficial da equipe. Fica numa pasta privada fora do git; nos relatórios aparece `***.456.789-**`.
  Não envie CPF por e-mail aberto ou grupo; envie a planilha direto na sessão.
- **Sem assinaturas:** tudo bem. Use como prova o que existir (e-mail do fiscal, ata, mensagem, "registro do gestor em AAAA-MM-DD").
  O relatório mostra a prova usada. A UST só conta como **ACEITA** com algum documento do órgão; sem isso ela aparece como **COMPROVADA** (tecnicamente).

## Rateio (dividir o total entre a equipe)

Ex.: a semana fechou 250 UST. A fábrica divide entre quem **tem participação registrada** naquela semana:
- por área (BACKEND, FRONTEND, DADOS…), conforme o módulo trabalhado;
- por peso do tipo de participação (conduzir 3, corrigir 2, revisar/orientar/aprovar 1);
- por senioridade (sênior ×1,5, pleno ×1, júnior ×0,7);
- modo `senior_da_area`: a parte de cada área vai inteira para o profissional mais sênior que participou.
Ajuste os pesos em `RATEIO.yaml`. É divisão **interna** — não muda a medição do contrato.

## Arquivos CSV/YAML (alternativa à planilha)

Pasta `modelos_csv_yaml/`: `FORMULARIO_CONTRATO.yaml`, `PROFISSIONAIS_ENTRADA.csv`, `PARTICIPACOES.csv`, `RATEIO_TOTAIS.csv`, `RATEIO.yaml`,
`TABELA_UST.csv`, `PRODUCAO_HISTORICA.csv`, `OS_MODELO.yaml`, `GEC_TEMPLATE.md`, `MATRIZ_RASTREABILIDADE.md`.
Pasta `modelos_evidencia/`: os documentos de prova de cada módulo (preenchidos pelos agentes; vocês completam revisão humana e aceite).

## Documentos do contrato (PDF/DOCX)

Edital, TR, contrato e aditivos, OS assinadas, tabela de UST/PF, padrões técnicos do órgão, acesso ao repositório existente (se houver).
Ver `O_QUE_ENVIAR.md` e `COMO_INICIAR.md`.
