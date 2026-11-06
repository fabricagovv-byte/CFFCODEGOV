---
name: participacao-equipe
description: PARTICIPAÇÃO DA EQUIPE / DOCUMENTO DE PARTICIPAÇÃO / IMPORTAR PARTICIPAÇÃO — gera por contrato o documento (Word, papel timbrado) para o gestor marcar quem fez o quê em cada módulo (condução, correção, revisão, orientação, aprovação), importa o preenchido e passa a dividir as UST executadas de cada módulo entre quem participou, com a conta explicada nos relatórios.
---
# PARTICIPAÇÃO DA EQUIPE (G18 + G15)

1. Equipe cadastrada no contrato (nome e função bastam): `fabrica.py profissionais adicionar <C> --nome ... --funcao ...`.
2. Documento para preencher: `python3 fabrica/ferramentas/fabrica.py participacao modelo <C>`
   → `contratos/<C>/PARTICIPACAO_EQUIPE_<C>.docx` (uma tabela por pessoa, módulos já listados). Entregue com SendUserFile.
3. Preenchido: `python3 fabrica/ferramentas/fabrica.py participacao importar <C> <arquivo.docx|csv>`
   → acrescenta em `PARTICIPACOES.csv` (sem duplicar). Sem prova escrita, a evidência fica "registro do gestor em <data>".
4. `fabrica.py relatorio tecnico <C>` passa a mostrar, por módulo e por pessoa, as UST atribuídas e a conta
   (UST do módulo × peso da pessoa ÷ soma dos pesos; peso = tipo × senioridade, de `RATEIO.yaml`).
5. Nunca preencha participação por conta própria: só o que o gestor marcar no documento ou disser na conversa.
   A divisão é interna: não muda a medição nem o aceite. Para o órgão sem a divisão: `relatorio tecnico <C> --sem-divisao`.
