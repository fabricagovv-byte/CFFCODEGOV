# O que você precisa me enviar (checklist)

Envie o que tiver. O Analista de Editais (G02) lê tudo e depois pergunta **só o que faltar**.

## 1. Documentos do contrato (PDF ou DOCX)

| # | Documento | Obrigatório? | Para quê |
|---|---|---|---|
| 1 | Edital e anexos | sim | exigências, equipe, tecnologias |
| 2 | Termo de Referência (TR) | sim | catálogo de serviços, medição, SLA, aceite |
| 3 | Contrato assinado e aditivos | sim | vigência, valores, obrigações |
| 4 | Ordens de Serviço (OS) | sim, para executar | o que fazer agora e quem autorizou |
| 5 | Tabela de UST / pontos de função / horas | sim | medir a produção |
| 6 | Documentos técnicos do órgão (padrões, arquitetura, manuais) | se houver | seguir o padrão do órgão |
| 7 | Acesso ao repositório existente | se houver | manutenção/evolução |

## 2. Planilhas para preencher (modelos em `fabrica/templates/`)

| Arquivo | O que preencher | Exemplo de linha |
|---|---|---|
| `PROFISSIONAIS.csv` | equipe real designada | `P01,Maria Souza,Gerente de Projeto,PMP + 8 anos,PMP 123,Planejamento,TODOS,maria@empresa.com.br,2026-01-01,` |
| `PARTICIPACOES.csv` | o que cada pessoa fez (revisou, corrigiu, aprovou), com prova | `2026-11-03,P02,OS-001,MOD-001,REVISAO,Revisou login,PR #12,` |
| `TABELA_UST.csv` | itens do catálogo do TR, exatamente como no contrato | `UST-DEV-03,Desenvolvimento alta complexidade,UST,24,ALTA,TR item 5.3,` |
| `PRODUCAO_HISTORICA.csv` | produção já **aceita** em meses anteriores, por profissional | `P02,2026-09,OS-014,UST-DEV-03,ALTA,24,Termo 014/2026` |

## 3. Dados do formulário (`contratos/<ID>/contrato.yaml`)

São 25 grupos: órgão, número do contrato, processo, edital, objeto, vigência, prazo, OS, modalidade de medição,
quantidades, tabela, critérios de aceite, profissionais, funções, responsabilidades, qualificações, tecnologias,
repositório, banco de dados, infraestrutura, integrações, homologação, produção, segurança e **autorização para executar**.

Para ver o que ainda falta: `python3 fabrica/ferramentas/fabrica.py contrato faltantes <ID>`.

## 4. Autorizações (sem elas a fábrica não executa)

- OS autorizada: quem autorizou, data e documento (nº da OS assinada).
- Publicação em produção: autorização separada (`pode_publicar_producao: true`) + confirmação na conversa.

## 5. Como enviar pelo celular

1. Anexe os PDFs na conversa (ou suba no repositório em `contratos/<ID>/documentos/`).
2. Diga: **"NOVO CONTRATO <ID>"**.
3. Responda às perguntas dos campos faltantes.
4. Diga: **"PLANEJAR CONTRATO <ID>"** e depois **"EXECUTAR OS <número>"**.
