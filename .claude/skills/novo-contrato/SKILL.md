---
name: novo-contrato
description: NOVO CONTRATO — recebe edital, TR, contrato, anexos, OS e tabela UST/PF, cria a pasta do contrato e apresenta só os campos que faltam no formulário. Use quando o usuário enviar documentos de uma nova contratação.
---
# NOVO CONTRATO (agentes G02 Analista de Editais, G03 Gestor Contratual)

1. `python3 fabrica/ferramentas/fabrica.py contrato novo <ID>` (ID curto, ex.: PMX-2026-014).
2. Copie os documentos recebidos para `contratos/<ID>/documentos/`. Leia TODOS integralmente (PDF: use a skill de PDF disponível; DOCX: a de DOCX).
3. Preencha `contrato.yaml` com o que encontrar, citando cláusula/página em comentário ao lado de cada valor.
4. Preencha `MATRIZ_RASTREABILIDADE.md` (uma linha por exigência, com origem). Registre conflitos entre documentos sem decidir por conta própria; registre-os com `python3 fabrica/ferramentas/fabrica.py decisao --por G02 --titulo "Conflito ..." --texto "..."` como PENDENTE de análise jurídica.
5. Copie a tabela de medição para `TABELA_UST.csv` exatamente como está no TR (não converta UST/PF/horas).
6. Rode `python3 fabrica/ferramentas/fabrica.py contrato faltantes <ID>` e apresente ao usuário SOMENTE os campos faltantes, agrupados, em linguagem simples. Se não houver formulário interativo, indique o arquivo `contratos/<ID>/contrato.yaml` para preencher e `PROFISSIONAIS.csv` para a equipe.
7. Verifique a legislação aplicável conforme o ente e a data (ver fabrica/legislacao/REFERENCIAS.md). Não presuma aplicação uniforme.
