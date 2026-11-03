# Como a produção é medida (UST, pontos de função e horas)

## Princípio

A quantidade que pode ser cobrada é **a que o contrato define**, comprovada por evidências e **aceita pelo órgão**.
A fábrica separa sempre três números:

| Número | O que significa | Quem define |
|---|---|---|
| **Previsto** | quantidade da OS para o item da tabela | OS assinada |
| **Comprovado** | previsto, se o módulo passou na auditoria técnica (código no git, testes reais sem falha, 15 evidências) | CLI (`fabrica.py medir`) |
| **Aceito** | quantidade do termo de recebimento do órgão | fiscal/gestor do contratante (registrado em `ACEITE.md`) |

## UST (Unidade de Serviço Técnico)

- Cada contrato tem um **catálogo de serviços** no TR: atividade → complexidade → quantidade de UST.
- O valor da UST, a fórmula e o que conta como entregue **estão no contrato**; a fábrica não cria fatores.
- Há jurisprudência do TCU com ressalvas ao uso de UST sem catálogo objetivo e sem relação com resultado; o G02 deve verificar os acórdãos e normas aplicáveis ao seu órgão antes de planejar a medição.

## Pontos de função

- Contagem pela metodologia do contrato (IFPUG CPM, NESMA ou o Roteiro de Métricas do SISP, por exemplo).
- O G16 monta a memória: fronteira, funções de dados (ALI/AIE), transacionais (EE/SE/CE), complexidade, total.
- Se o contrato exigir contador certificado (CFPS/CFPP), a contagem precisa da revisão dele.

## Medição por catálogo de serviços, perfis e horas

Quando o edital define perfis (valor/hora, fator UST) e horas por serviço:

1. `PERFIS.csv`: perfil, valor_hora, fator_ust_por_hora, referência (cláusula).
2. `CATALOGO_SERVICOS.csv`: serviço → horas de cada perfil (e UST por serviço, se o edital der).
3. `contrato.yaml` → `medicao.formula`: `UST_POR_SERVICO` (soma a UST do catálogo), `HORAS_X_FATOR` (horas × fator de cada perfil) ou `HORAS`.
4. Na OS, cada módulo lista `servicos: [{codigo, quantidade}]`. A medição mostra horas por perfil, quantidade e valor (R$).
5. Sem fórmula declarada, a fábrica não converte nada.

## Horas

Só quando o contrato medir por horas, e só com registro de horas **declarado pelo próprio profissional**.
A fábrica nunca gera horas.

## "UST média de um trabalho difícil" e separação por profissional

Isso sai dos **seus dados históricos**, não de uma tabela inventada:

1. Preencha `PRODUCAO_HISTORICA.csv` com o que já foi **aceito** (profissional, mês, OS, item, complexidade, UST aceita, termo).
2. Rode `python3 fabrica/ferramentas/fabrica.py producao estatisticas PRODUCAO_HISTORICA.csv`.
3. Resultado: por profissional e complexidade (BAIXA/MEDIA/ALTA), número de OS, total, média, mínimo e máximo de UST aceita por OS.

Use essas médias **para planejar** (capacidade da equipe, prazo). Para faturar, vale só a medição da OS.

## Saldo e fechamento diário

- **Saldo oficial** = quantidade contratada (contrato.yaml `medicao.quantidade_contratada`) − aceito.
- **Saldo projetado** = contratado − comprovado (o que já foi produzido e auditado, ainda sem aceite).
- `fabrica.py saldo <C>` mostra os dois, o consumo e, com histórico de fechamentos, a média diária e em quantos dias o saldo acaba.
- `fabrica.py fechamento <C> --data AAAA-MM-DD`: quem trabalhou, produção do dia, divisão por pessoa e saldo. Para todos os projetos: `fabrica.py portfolio <repos...> --data AAAA-MM-DD`.

## Rateio por período (ex.: 250 UST na semana divididas entre a equipe)

1. Registre o total do período em `RATEIO_TOTAIS.csv` (`semanal,2026-11-02,250,aceito,<documento>`) — ou passe `--total 250`.
2. Registre em `PARTICIPACOES.csv` quem fez o quê naquele período (com prova).
3. `fabrica.py rateio semanal <C> --data 2026-11-02` (ou o relatório semanal, que já traz a seção de rateio).
4. Regra em `RATEIO.yaml`: pesos por tipo de participação × senioridade, separado por área; modo `senior_da_area` atribui a parte da área ao mais sênior que participou.
5. Só entra quem tem participação registrada no período. Sem participação: nada é atribuído (aparece "não atribuído").
6. É divisão gerencial interna. Não altera a memória de cálculo contratual.

## Por profissional no mês

- O responsável técnico de cada módulo fica em `RESPONSAVEIS.md` (`responsavel_tecnico: P02`).
- A participação real (condução, orientação, revisão, correção, aprovação) fica em `PARTICIPACOES.csv`, sempre com prova (commit, PR, ata).
- `fabrica.py relatorio profissional <C> --profissional P02 --data 2026-11-01` gera o relatório do mês daquela pessoa.
- Participação sem prova é rejeitada pela CLI.

## Entrega e conferência mensal

1. Dia a dia: `relatorio diario`.
2. Fim do mês: `medir` para cada OS → `relatorio mensal` → `checklist` → `entrega`.
3. Envie ao fiscal: relatório mensal + memória de cálculo + pacote de evidências.
4. Quando o órgão emitir o termo, registre em `ACEITE.md` e rode `medir` de novo: o "aceito" passa a contar.
