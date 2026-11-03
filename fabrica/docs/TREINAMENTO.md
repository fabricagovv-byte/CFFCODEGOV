# Treinamento — Fábrica de Software Governamental

Manual para quem vai operar a fábrica e para qualquer chat (Claude Code ou Codex) que for trabalhar num repositório da fábrica.
Leia uma vez do começo ao fim. Depois use como consulta: Parte 4 (jornada), Parte 11 (frases), Parte 13 (o que você recebe todo dia), Parte 15 (limites) e Parte 16 (problemas).

## Parte 1 — O que é a fábrica

- **Agentes de IA (44):** fazem o trabalho técnico e administrativo: leem o edital, planejam, programam, testam, revisam, documentam, auditam, medem e geram relatórios. Cada um tem uma função (lista em `fabrica/docs/EQUIPE_AGENTES.md`).
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
PREPARAR PUBLICAÇÃO · PUBLICAR PRODUÇÃO · CRIAR REPOSITÓRIO · CRIAR REPOSITÓRIOS · PORTFÓLIO · FECHAMENTO DE TODOS OS PROJETOS ·
ANÁLISE INTEGRAL DO EDITAL · GEC · QUANTO EU PRODUZO · FLUXO DA OS · CONFIGURAR FÁBRICA · ESPECIFICAR MÓDULO · CONTINUE O FLUXO

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

## Parte 13 — O que você recebe todo dia (entrada e saída)

| Momento | Você diz | Você recebe (Word) | Para que serve |
|---|---|---|---|
| **Entrada** (manhã) | "ABERTURA DO DIA" | contratado, consumo, saldo, equipe, o que está planejado hoje por projeto/módulo, **meta do dia** em UST e horas, tarefas e bloqueios | combinar o dia com a equipe |
| Durante | "EXECUTAR OS …" / "FLUXO DA OS …" | código, testes, capturas, evidências | produzir |
| **Saída** (fim do dia) | "RELATÓRIO DIÁRIO" e "FECHAMENTO DO DIA" | o que foi feito de verdade: commits, tarefas, testes, quem trabalhou, medição do dia, divisão por pessoa, saldo | prestar contas, base do mensal |
| Semana | "RELATÓRIO SEMANAL" (+ total, se houver) | consolidado + rateio | acompanhamento |
| Mês | "RELATÓRIO MENSAL", "GEC", "PREPARAR ENTREGA" | medição, mensalidade, checklist, pacote ZIP | faturamento (após aceite) |

## Parte 14 — As regras, explicadas (por quê)

| Regra | Por quê | Se faltar |
|---|---|---|
| Nada inventado | O órgão e o TCU auditam; dado falso é responsabilidade da empresa | aparece "sem registro" |
| Evidência antes de afirmação | Já aconteceu de "passar" sem rodar; só vale o comando executado | a IA roda de novo antes de afirmar |
| OS só com autorização | Executar sem OS não é pago e pode ser irregular | o fluxo **pausa** em "autorização" |
| UST/PF/horas só pela fórmula do contrato | Conversão inventada é sobrepreço | a medição é recusada |
| Comprovado ≠ aceito | Só o aceite do órgão vira pagamento | saldo oficial não muda |
| CPF fora do git | LGPD | o CPF fica só na pasta privada |
| Estimativa ≠ real | Planejar não é produzir | os documentos marcam ESTIMATIVA e REAL |
| TDD, depuração, revisão | Menos retrabalho e glosa | o módulo não passa na auditoria |
| O edital manda | Cada órgão nomeia e exige diferente | ajuste em EDITAL.yaml e tudo segue |

## Parte 15 — Limites (o que a fábrica não faz, e quem faz)

| A fábrica NÃO… | Quem faz |
|---|---|
| assina documentos, declara aceite ou atesta participação | profissionais e órgão |
| envia nada ao órgão (e-mail, protocolo, sistema) | preposto/gestor |
| publica em produção sem autorização registrada | gestor + autorização |
| acessa sistemas do órgão sem credencial fornecida por vocês | vocês fornecem acesso |
| dá parecer jurídico final ou decide conflito entre documentos | jurídico/gestor |
| garante aceite, prazo do órgão ou resultado de licitação | — |
| guarda arquivos fora do repositório: o ambiente na nuvem é descartável; o que importa vai por commit/push | a IA faz o push ao terminar |
| converte unidades ou conta trabalho duas vezes | — |

Os limites estão em `fabrica/CONFIGURACAO_FABRICA.yaml` → `limites` (só podem ficar mais restritivos).

## Parte 16 — Problemas: o que você fala

| Situação | O que dizer |
|---|---|
| Não sei onde parei | "PRÓXIMO PASSO" |
| Quero tudo da OS de uma vez | "FLUXO DA OS OS-001" |
| O fluxo parou | "por que o fluxo parou? corrija e retome" |
| O fluxo pausou para aprovação | verifique os itens e diga: "aprovado por <nome, cargo>, continue o fluxo" |
| Um teste falhou | "depure com depuração sistemática e me mostre a causa" |
| O edital mudou ou saiu aditivo | "atualize EDITAL.yaml com o aditivo <arquivo> e refaça o confronto e o GEC" |
| O órgão pediu outro nome de relatório | "o edital chama o mensal de RME: ajuste e gere de novo" |
| A equipe mudou | "atualize a equipe: entra X (cargo), sai Y" |
| Quero saber quanto produzo | "QUANTO EU PRODUZO" (ou "simule 3 devs plenos e 1 testador") |
| Recebi o aceite | "registre o aceite da OS-001: <documento>, <quantidade>" |
| Glosa ou atraso | "mostre os SLAs em risco e o que fazer" |
| Algo parece errado num número | "mostre a memória de cálculo de <item>" |

## Parte 17 — Nomes só no final

Pode trabalhar o contrato inteiro **sem nomes**: o planejamento usa os **perfis** (ex.: DESENVOLVEDOR_PLENO) e os relatórios mostram "a cadastrar".
Antes da entrega, envie o Word **Nome, CPF, Cargo** e diga "IMPORTAR EQUIPE". A partir daí, entram nos relatórios os responsáveis, a capacidade real e o rateio por pessoa.
Participações e aceites **anteriores** ao cadastro não são inventados: o que não foi registrado continua "sem registro".

## Parte 18 — Configuração central

Um arquivo só: `fabrica/CONFIGURACAO_FABRICA.yaml` (empresa, fuso, horas por dia, aproveitamento, feriados, produtividade h/PF, relatórios do dia, rateio, stacks preferidas, limites).
Diga "CONFIGURAR FÁBRICA" e responda às perguntas; para conferir: "verifique a configuração".

## Parte 19 — Quanto eu produzo? (capacidade)

"QUANTO EU PRODUZO" calcula por pessoa, por dia e por mês: horas, UST, PF e valor. Tudo é **estimativa**.

```
horas produtivas/dia = horas por dia × aproveitamento                  (ex.: 8 × 0,8 = 6,4 h)
UST/dia              = horas produtivas × fator UST do perfil (contrato) (ex.: 6,4 × 1,3 = 8,32 para dev sênior)
PF/dia               = horas produtivas ÷ produtividade (h/PF)         (ex.: 6,4 ÷ 10 = 0,64 PF)
valor/dia            = horas produtivas × valor/hora do perfil
```

Exemplo do TESTE-002 (fictício): 1 dev sênior, 2 plenos, 1 analista de requisitos e 1 de testes = **32 h, 34,56 UST e R$ 3.296,00 por dia**, ou **725,76 UST e R$ 69.216,00 por mês** (21 dias úteis).
Para PF, informe a produtividade (h/PF) do contrato ou do seu histórico. Com o PRODUCAO_HISTORICA.csv preenchido, o relatório compara a estimativa com o que já foi **aceito**.

## Parte 20 — Análise integral do edital e GEC

1. Envie todos os PDFs e diga "ANÁLISE INTEGRAL DO EDITAL <ID>". Os 24 agentes da Fábrica Governamental leem tudo e registram, **com cláusula e página**:
   - a explicação técnica de cada serviço;
   - os profissionais exigidos;
   - os documentos de habilitação;
   - os SLAs e as glosas;
   - as regras de medição (UST, PF, horas);
   - o pagamento, os relatórios exigidos e os prazos.
2. Você preenche o PLANEJAMENTO (ou pede uma sugestão, que você aprova).
3. "GEC <ID>" gera o **Plano de Gestão da Execução Contratual em Word**, com 17 seções:
   - identificação, objeto e serviços explicados;
   - equipe exigida × designada e responsáveis;
   - plano por projeto, cronograma diário e mensal, mensalidades;
   - medição e custos;
   - habilitação, SLAs, relatórios e riscos;
   - ESTIMATIVA × REAL e pendências.
4. O que não consta no edital aparece como "a preencher" ou "não consta". A fábrica pergunta em vez de inventar.

## Parte 21 — Fluxo automático da OS

"FLUXO DA OS OS-001" faz, nesta ordem: autorização → testes → commits → auditoria → medição → relatórios → checklist → entrega.
- Cada etapa fica salva. Se parar (falha) ou pausar (precisa de pessoa), diga "continue o fluxo": ele retoma exatamente de onde parou.
- Ele **pausa** em dois casos: falta a autorização da OS, ou há controles críticos que só uma pessoa pode verificar.

## Parte 22 — Conhecimento incorporado (como a fábrica trabalha por dentro)

| Disciplina | Origem | O que muda para você |
|---|---|---|
| Evidência antes de afirmação | Superpowers | a IA só diz "pronto" mostrando o resultado do teste |
| TDD (teste antes do código) | Superpowers | menos defeitos na homologação |
| Depuração sistemática | Superpowers | erro corrigido pela causa, não "no chute" |
| Plano em passos pequenos + execução com revisão em 2 etapas | Superpowers | entregas previsíveis |
| Especificação orientada (spec → plano → tarefas) | spec-kit (GitHub) | cada módulo nasce rastreado ao edital |
| Fluxo durável com pausa humana | LangGraph (conceitos) | "FLUXO DA OS" retoma e pede aprovação |
| Testes de tela, design acessível, integrações MCP, criação de skills | Skills da Anthropic (Apache 2.0) | telas melhores e integrações seguras |

Os originais e as licenças estão em `fabrica/conhecimento/`.

## Anexo A — Prompt inicial (cole em qualquer chat novo)

```
Você é a Fábrica de Software Governamental deste repositório. Antes de tudo:
1) Leia AGENTS.md e siga as regras inegociáveis (nada inventado; evidência antes de afirmar; OS só com autorização; UST/PF/horas só pela fórmula do contrato; CPF fora do git; estimativa separada do real).
2) Rode: python3 fabrica/ferramentas/fabrica.py agentes gerar && python3 fabrica/ferramentas/fabrica.py iniciar
3) Rode: python3 fabrica/ferramentas/fabrica.py proximo-passo   (ou com o ID do contrato)
4) Me diga em poucas linhas: o que está pronto, o que falta e a próxima ação.
Responda em português, de forma simples. Gere os relatórios também em Word. Faça commit e push do que produzir.
Meu pedido agora: <escreva aqui>
```
