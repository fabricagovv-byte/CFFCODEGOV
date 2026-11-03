# Treinamento — Fábrica de Software Governamental

Manual para quem vai operar a fábrica e para qualquer chat (Claude Code ou Codex) que for trabalhar num repositório da fábrica.
Leia uma vez do começo ao fim. Depois use a Parte 4 (jornada) e a Parte 11 (frases) como consulta.

## Parte 1 — O que é a fábrica

- **Agentes de IA (40):** fazem o trabalho técnico e administrativo: leem o edital, planejam, programam, testam, revisam, documentam, auditam, medem e geram relatórios. Cada um tem uma função (lista em `fabrica/docs/EQUIPE_AGENTES.md`).
- **Profissionais reais (vocês):** designam a equipe, fazem o planejamento, autorizam as ordens de serviço, revisam e aprovam o que os agentes fizeram e falam com o órgão.
- **Provas:** tudo que a fábrica afirma tem prova: commit no git, teste executado, captura de tela, registro de quem revisou. O que não tem prova aparece como "sem registro".
- **Um repositório por sistema.** Cada sistema (até 30 ou mais) tem o seu repositório, criado a partir do modelo da fábrica.

## Parte 2 — Preparação (uma vez)

1. **Criar o repositório do sistema:** descompacte `CONFIGURACAO_FABRICA.zip`, renomeie a pasta com o ID do sistema (ex.: `pmx-001-sgd`) e suba como repositório privado no GitHub. Para muitos sistemas de uma vez: aba PROJETOS do Documento Base e a frase "CRIAR REPOSITÓRIOS".
2. **Abrir uma sessão:** no app do Claude (Claude Code), escolha o repositório e abra uma conversa nova. No Codex, abra o repositório.
3. **Colar o prompt inicial** (Anexo A) ou só dizer **"INICIAR FÁBRICA"**.
4. **Gerador de Word:** na primeira vez, peça "prepare o gerador de Word" (o chat roda `npm install --prefix fabrica/ferramentas`).

A qualquer momento, diga **"PRÓXIMO PASSO"**: o chat confere tudo e diz o que falta, em ordem.

## Parte 3 — O que vocês preenchem

| Arquivo | O que pôr | Quando |
|---|---|---|
| `EQUIPE_NOME_CPF_CARGO.docx` | Nome, CPF e cargo de cada pessoa (mínimo: nome e cargo) | no início e quando a equipe mudar |
| `DOCUMENTO_BASE.xlsx` → EMPRESA | razão social, CNPJ, responsável legal, preposto | uma vez |
| `DOCUMENTO_BASE.xlsx` → CAPACIDADES | tecnologias, certificações e atestados da empresa | uma vez, atualizar quando mudar |
| `DOCUMENTO_BASE.xlsx` → PERFIS e CATALOGO_SERVICOS | perfis do órgão (valor/hora, fator UST) e horas por serviço, **copiados do edital** | por contrato |
| `DOCUMENTO_BASE.xlsx` → TABELA_UST | catálogo de serviços do TR (se o contrato mede só por UST) | por contrato |
| `DOCUMENTO_BASE.xlsx` → PLANEJAMENTO | **o seu plano:** projeto, módulo, serviço, quantidade, início, fim, responsável | por contrato e quando replanejar |
| `DOCUMENTO_BASE.xlsx` → PARTICIPACOES | quem conduziu, corrigiu, revisou ou aprovou o quê, com a prova | toda semana (ou todo dia) |
| `DOCUMENTO_BASE.xlsx` → RATEIO_TOTAIS | total de UST do dia, semana ou mês para dividir entre a equipe | quando houver total fechado |
| PDFs | edital, termo de referência, contrato, aditivos, ordens de serviço | no início de cada contrato/OS |

**Regras do preenchimento**
- Copie números e nomes **exatamente** como estão no edital.
- Linhas que começam com `#` são exemplos e são ignoradas.
- O CPF fica fora do git. Nos relatórios ele aparece mascarado (`***.456.789-**`).
- Não tem assinatura? Use outra prova: e-mail do fiscal, ata ou "registro do gestor em AAAA-MM-DD".

## Parte 4 — Jornada de um contrato, do começo ao fim

| # | Você diz (no chat) | A fábrica faz | Você recebe |
|---|---|---|---|
| 1 | "NOVO CONTRATO CT-12-2026" + PDFs | cria `contratos/CT-12-2026/`, guarda os documentos | confirmação |
| 2 | "ANALISAR EDITAL CT-12-2026" | lê tudo, monta matriz de exigências e `EDITAL.yaml` (com cláusulas) | resumo do edital |
| 3 | "O QUE FALTA NO CONTRATO CT-12-2026" | lista os campos não encontrados | perguntas curtas |
| 4 | envia Word da equipe + Documento Base → "IMPORTAR EQUIPE" / "IMPORTAR DOCUMENTO BASE" | cadastra pessoas (CPF protegido), empresa, capacidades, perfis, catálogo, plano | contagem e erros |
| 5 | "CONFRONTAR EDITAL CT-12-2026" | cruza edital × documento base | ✔ atende · ⚠ ajustar · ✘ falta (Word) |
| 6 | "PLANEJAMENTO CT-12-2026" | calcula por projeto: UST, horas por perfil, valor, prazo, capacidade, saldo | Plano de Projetos (Word) |
| 7 | "PPJ CT-12-2026" | Planejamento de Projeto Sustentável | PPJ (Word) |
| 8 | "GERAR OS DO PROJETO ATENDIMENTO" | cria a OS a partir do seu plano (sem autorização) | rascunho da OS |
| 9 | "AUTORIZO A OS-001: autorizada por <nome/cargo> em <data>, documento <nº>" | registra a autorização | OS liberada |
| 10 | "EXECUTAR OS-001" | código real por módulo (CRUD completo: banco, API, tela, testes), revisão, segurança, commits | resumo + provas |
| 11 | "AUDITAR EVIDÊNCIAS" e "MEDIR PRODUÇÃO OS-001" | confere provas e mede pelo contrato | memória de cálculo (Word) |
| 12 | (diário) "ABERTURA DO DIA" → trabalho → "RELATÓRIO DIÁRIO" → "FECHAMENTO DO DIA" | os três relatórios do dia | 3 Word por dia |
| 13 | (fim do mês) "RELATÓRIO MENSAL", "RATEIO MENSAL", "PREPARAR ENTREGA OS-001" | consolida, divide por pessoa, checklist de 100 controles, pacote | ZIP de entrega + Word |
| 14 | "REGISTRE O ACEITE: <documento do órgão>" | grava o aceite e mede de novo | UST passa a "aceita" |
| 15 | "PREPARAR PUBLICAÇÃO" → autorização → "PUBLICAR PRODUÇÃO" | plano de implantação; publica só com autorização | sistema no ar |

## Parte 5 — Rotina

| Quando | O que fazer |
|---|---|
| Começo do dia | "ABERTURA DO DIA": contratado, saldo, equipe e o que está planejado para hoje (meta em UST/horas) |
| Durante o dia | "EXECUTAR OS…", "GERAR CRUD …", "VERIFICAR CÓDIGO"; registre participações (quem revisou, corrigiu, aprovou) |
| Fim do dia | "RELATÓRIO DIÁRIO" e "FECHAMENTO DO DIA" (informe a produção do dia, se tiver: "hoje fechou 40 UST") |
| Toda semana | "RELATÓRIO SEMANAL"; se tiver o total: "a semana de 02/11 fechou 250 UST" → "RATEIO SEMANAL" |
| Fim do mês | "MEDIR PRODUÇÃO", "RELATÓRIO MENSAL", "RATEIO MENSAL", "PREPARAR ENTREGA", enviar ao fiscal |
| Vários sistemas | "FECHAMENTO DE TODOS OS PROJETOS" (portfólio: saldo e produção de cada repositório) |

## Parte 6 — Medição explicada

- **Previsto:** o que a OS prevê.
- **Comprovado:** o que foi feito e passou na auditoria (código no git, testes sem falha, evidências completas).
- **Aceito:** o que o órgão aceitou por documento. Só esse vira faturamento.
- **Saldo oficial** = contratado − aceito. **Saldo projetado** = contratado − comprovado.
- **Por hora e perfil:** cada serviço tem horas por perfil, e cada perfil tem valor/hora e fator UST. A fórmula vem do contrato (`UST_POR_SERVICO`, `HORAS_X_FATOR` ou `HORAS`). Sem fórmula, a fábrica não converte.
- **Rateio por pessoa:** divide o total do período entre quem tem participação registrada, por área e senioridade (ou tudo para o sênior da área). É divisão interna e não muda a medição.
- **Produzir mais:** use "OPORTUNIDADES DE MEDIÇÃO" (trabalho real que não está sendo medido), divida OS grandes, reduza retrabalho. Nunca aumente número sem trabalho real.

## Parte 7 — Gerar código real

1. Descreva o cadastro (ou deixe o chat propor a partir do edital): campos, tipos, obrigatórios, únicos, dados pessoais, quem pode ver, alterar e excluir.
2. "GERAR CRUD <nome>": gera tabela, migração, API com validações, auditoria, permissão por perfil, tela com busca e formulário, testes de API e de tela, tudo na pasta do módulo.
3. A prova é obrigatória: testes no PostgreSQL, migração conferida contra o modelo, build e testes da tela, captura de tela real.
4. Regras específicas do edital (cálculos, fluxos, integrações) são programadas em cima da base gerada e também precisam de testes.
5. Linguagem exigida pelo edital: "CRIAR REPOSITÓRIO … com stack java-spring" (ou dotnet, php, go, node, rust, react). Base completa pronta para cadastros: stack `sistema-gov`.

## Parte 8 — Muitos sistemas (ex.: 30)

- Um repositório por sistema, todos a partir do mesmo modelo. A aba PROJETOS do Documento Base cria todos de uma vez.
- Use o mesmo ID de pessoa (P01…) em todos os repositórios, para o portfólio somar certo.
- Visão geral: "PORTFÓLIO" ou "FECHAMENTO DE TODOS OS PROJETOS".
- Melhorou a fábrica? Copie só `AGENTS.md`, `CLAUDE.md`, `.claude/` e `fabrica/` (exceto `fabrica/comunicacao/`) para cada repositório.

## Parte 9 — O que a fábrica nunca faz

1. Inventar commit, teste, captura, horas, participação, assinatura ou aceite.
2. Executar OS sem autorização registrada ou publicar em produção sem autorização.
3. Converter UST, pontos de função e horas sem fórmula do contrato, ou contar o mesmo trabalho duas vezes.
4. Guardar CPF no git ou mostrá-lo completo fora do documento oficial restrito.
5. Afirmar que cumpre lei, norma ou certificação sem prova.

## Parte 10 — Problemas comuns

| Sintoma | O que fazer |
|---|---|
| "Não sei onde parei" | "PRÓXIMO PASSO" |
| Relatório sem Word | "prepare o gerador de Word" (npm install) |
| Medição recusada: "defina medicao.formula" | informe a fórmula do edital (ou use a TABELA_UST) |
| "OS sem autorização" | registre quem autorizou, a data e o documento |
| Capacidade "sem pessoa no perfil" | cadastre a equipe com cargos que correspondam aos perfis do catálogo |
| UST "comprovada" mas não "aceita" | falta o documento de aceite do órgão |
| Teste falhou | o chat corrige o código e roda de novo; não há entrega com teste falhando |
| Docker não sobe por limite de download | use um espelho de registro ou tente mais tarde |
| Chat novo sem contexto | cole o prompt inicial (Anexo A) |

## Parte 11 — Frases que o chat entende

INICIAR FÁBRICA · PRÓXIMO PASSO · NOVO CONTRATO · ANALISAR EDITAL · O QUE FALTA NO CONTRATO · IMPORTAR EQUIPE ·
IMPORTAR DOCUMENTO BASE · CONFRONTAR EDITAL · CONFIGURAR MEDIÇÃO · PLANEJAMENTO · PPJ · GERAR OS DO PROJETO · EXECUTAR OS ·
GERAR CRUD · VERIFICAR CÓDIGO · AUDITAR EVIDÊNCIAS · MEDIR PRODUÇÃO · OPORTUNIDADES DE MEDIÇÃO · ABERTURA DO DIA ·
RELATÓRIO DIÁRIO · FECHAMENTO DO DIA · RELATÓRIO SEMANAL · RELATÓRIO MENSAL · RATEIO · SALDO · PREPARAR ENTREGA ·
PREPARAR PUBLICAÇÃO · PUBLICAR PRODUÇÃO · CRIAR REPOSITÓRIO · CRIAR REPOSITÓRIOS · PORTFÓLIO · FECHAMENTO DE TODOS OS PROJETOS

Os comandos técnicos equivalentes (`python3 fabrica/ferramentas/fabrica.py …`) estão em `fabrica/docs/GUIA_PASSO_A_PASSO.md`.

## Parte 12 — Exercício prático (30 minutos)

Faça no repositório de origem, que já tem o TESTE-002 completo:

1. "PRÓXIMO PASSO TESTE-002". Veja as etapas prontas e as que faltam.
2. "PLANEJAMENTO TESTE-002". Abra o Word: dois projetos, horas por perfil, alertas de capacidade.
3. "ABERTURA DO DIA TESTE-002 de 03/11/2026". Confira a meta do dia (35,35 UST).
4. Cadastre duas pessoas: "adicione Ana Souza, Desenvolvedora Sênior, e Beto Lima, Analista de Testes, no TESTE-002". Rode o PLANEJAMENTO de novo e veja a capacidade mudar.
5. Registre uma participação: "Ana revisou o MOD-101 em 03/11, prova: commit do MOD-101". Gere o FECHAMENTO DO DIA e veja o nome dela.
6. "a semana de 02/11 fechou 80 UST" → "RATEIO SEMANAL TESTE-002". Veja a divisão.
7. "GERAR CRUD de Setores com nome, sigla única e responsável". Confira os testes passando.
8. "PREPARAR ENTREGA OS-TESTE-002". Abra o ZIP e o checklist de 100 controles.

## Anexo A — Prompt inicial (cole em qualquer chat novo)

```
Você é a Fábrica de Software Governamental deste repositório. Antes de tudo:
1) Leia AGENTS.md e siga as regras inegociáveis (nada inventado; OS só com autorização; UST/PF/horas só pela fórmula do contrato; CPF fora do git).
2) Rode: python3 fabrica/ferramentas/fabrica.py agentes gerar && python3 fabrica/ferramentas/fabrica.py iniciar
3) Rode: python3 fabrica/ferramentas/fabrica.py proximo-passo   (ou com o ID do contrato)
4) Me diga em poucas linhas: o que está pronto, o que falta e a próxima ação.
Responda em português, de forma simples. Gere os relatórios também em Word. Faça commit e push do que produzir.
Meu pedido agora: <escreva aqui>
```
