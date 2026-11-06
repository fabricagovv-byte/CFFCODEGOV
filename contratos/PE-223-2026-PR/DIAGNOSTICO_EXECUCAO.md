# Diagnóstico de execução — Edital PE 223/2026 (Paraná) e Laboratório DIGITALGOV V3

Gerado em 06/11/2026 pela fábrica (agentes G02, G05, G21, G22 e G23 leram as 223 páginas). Toda afirmação cita a página do edital. Revisão humana pendente.

> **Atenção ao prazo:** a sessão do pregão é em **11/11/2026, às 10h** (p. 1). Os documentos de habilitação devem ser enviados em **1 dia útil** após a convocação (p. 173).

## 1. O edital em uma página

| Item | O que diz | Página |
|---|---|---|
| Órgão | Estado do Paraná — SEAP/DECON/Departamento de Logística | p. 1 |
| Processo / pregão | Protocolo 24.481.744-0 · Pregão Eletrônico 223/2026 · Compras.gov 36/2026 · UASG 928658 | p. 1 |
| Julgamento | Menor preço, disputa aberta | p. 1-2 |
| Regime | Lei 14.133/2021, Decreto Estadual 10.086/2022, LC 123/2006 | p. 1 |
| Vigência | 12 meses, prorrogável (arts. 106-107 da Lei 14.133) | p. 99 |
| Medição | UST base × fator de complexidade 1 (júnior), 2 (pleno) ou 3 (sênior), por Ordem de Serviço | p. 19-22 |
| Volume | 130.000 UST base/ano = 325.000 UST ajustadas (referencial; sem mínimo) | p. 136, 183 |
| Catálogo detalhado | ainda não existe: será pactuado entre contratante e contratada | p. 22 |
| Pagamento | mensal, após validação do gestor; até 30 dias do atesto; glosas descontadas | p. 59, 66, 143 |
| Valor estimado | não consta no edital (documento separado) | p. 60 |

## 2. Os 15 serviços e a medição

| # | Serviço | Fator | UST base/ano | UST ajustadas | Laboratório (teste positivo / negativo) |
|---|---|---|---|---|---|
| 1 | Suporte técnico de 1º Nível | 1 | 10.000 | 10.000 | HTTP 201 / 400 |
| 2 | Suporte técnico de 2º Nível | 2 | 5.000 | 10.000 | HTTP 201 / 400 |
| 3 | Suporte técnico de 3º Nível | 3 | 10.000 | 30.000 | HTTP 201 / 400 |
| 4 | Sustentação de Sistemas | 2 | 20.000 | 40.000 | HTTP 201 / 400 |
| 5 | Desenvolvimento de Sistemas | 3 | 10.000 | 30.000 | HTTP 201 / 400 |
| 6 | Testes de Sistemas | 2 | 5.000 | 10.000 | HTTP 201 / 400 |
| 7 | Análise de Negócios e Processos | 2 | 10.000 | 20.000 | HTTP 201 / 400 |
| 8 | Implementação DevOps | 3 | 5.000 | 15.000 | HTTP 201 / 400 |
| 9 | Business Intelligence e Ciência de Dados | 3 | 10.000 | 30.000 | HTTP 201 / 400 |
| 10 | Desenvolvimento de Inteligência Artificial | 3 | 10.000 | 30.000 | HTTP 201 / 400 |
| 11 | Gerenciamento de Projetos | 3 | 5.000 | 15.000 | HTTP 201 / 400 |
| 12 | Serviços para Jornada do Cidadão | 2 | 5.000 | 10.000 | HTTP 201 / 400 |
| 13 | Serviços de Governança de TI | 3 | 5.000 | 15.000 | HTTP 201 / 400 |
| 14 | Serviços de Gestão de Segurança da Informação | 3 | 10.000 | 30.000 | HTTP 201 / 400 |
| 15 | Serviços de Integração de Sistemas e Soluções Correlatas | 3 | 10.000 | 30.000 | HTTP 201 / 400 |
| | **Total** | | **130.000** | **325.000** | 15 de 15 responderam certo |

## 3. Laboratório DIGITALGOV V3 — o que foi executado

- **Testes reais:** 16 de 16 conjuntos passaram (15 serviços + central). Cada serviço tem **4 testes**; a central, 5.
- **Servidores:** painel (porta 8765) e 15 serviços (portas 8001 a 8015) subiram e responderam, todos restritos ao próprio computador.
- **Operação de cada serviço:** exemplo oficial aceito (HTTP 201) e dado inválido recusado com mensagem clara (HTTP 400). Respostas guardadas em `laboratorio/servicos/`.
- **Painel:** UST verificadas, aceitas e faturáveis = 0; as 15 OS estão marcadas como SIMULADAS; a cadeia de auditoria está íntegra.
- **O que é protótipo:** cada serviço é um demonstrador de **uma** operação (45 a 63 linhas), sem login nem perfis. Não são os sistemas exigidos pelo TR.
- **Subfunções que ainda NÃO existem:** praticamente todo o escopo de cada serviço no TR, por exemplo:
  - suporte: ITSM, base de conhecimento, SLA por chamado e atendimento presencial;
  - desenvolvimento: ciclo completo de requisitos, homologação e implantação;
  - BI/IA: fontes reais, painéis e modelos treinados;
  - integração: APIs institucionais, além das 4 soluções de software que o item 15 exige (ITSM, monitoramento, gestão de projetos e low-code) (p. 37-44).

## 4. Habilitação: o que pode eliminar

- **Atestados (p. 126-130):**
  - 20.000 UST em desenvolvimento;
  - 10.000 UST cada em Python, PHP, React/Next/Vue e suporte (5.000 delas num único contrato);
  - 5.000 UST cada em mobile, BI/ETL, N2 e N3;
  - no mínimo 20 aplicações em manutenção.
- **Maturidade (p. 128-131):** CMMI-DEV nível 3 ou MPS.BR C, ISO 20000, ISO 27001 e ISO 27701. Evidência com data autodeclarada **não** vale.
- **Econômico-financeiro (p. 125):** índices LG, SG e LC ≥ 1,0; patrimônio líquido ≥ 10% do valor anual.
- No total são 50 itens de habilitação. A lista completa está no GEC (seção 11) e em `analise_edital/g21.yaml`.

## 5. Prova de conceito: ponto decisivo

- **Quem faz:** só a 1ª colocada, depois de habilitada.
- **Como é:** presencial em Curitiba, durante 5 dias úteis, com demandas de no mínimo 500 UST (p. 97, item 24.3.22; p. 119).
- **Sem IA generativa:** a IA é **proibida** na prova (p. 93, item 24.2.8; p. 120, item 8.3), e a construção é manual, pela equipe indicada. A fábrica de IA serve para preparar e treinar a equipe, **não** para fazer a prova.
- **O que precisa ser entregue:** SSO/OAuth2 com login por CPF, ETL assíncrono com bases do IPARDES, Kubernetes com autoescala, CI/CD com rollback, Prometheus/Grafana, testes E2E e LGPD (p. 104-116).
- **Placar conservador da fábrica hoje** (63 requisitos): 0 atende · 0 parcial · 0 não atende. Nenhum dos itens críticos da p. 116 está atendido.

## 6. Riscos financeiros e de SLA

- **Base do preço:** não está claro se o preço incide sobre a UST base ou sobre a ajustada, uma diferença de 2,5 vezes (p. 135-136).
- **Sem volume mínimo:** o órgão pode suprimir até 25% (cláusula 14.1.1).
- **Garantia e multas:** garantia de 5% em 30 dias; multas de até 30% (cláusulas 11 e 12).
- **Caixa lento:** recebimento provisório em 30 dias + definitivo em 60 + pagamento em até 30.
- **SLA:** 26 indicadores de nível de serviço com glosa (p. 69-72). Lista completa no GEC (seção 12).

## 7. Equipe

- **Cadastrados só com nome e função:** Jerlian, Ruan, Arthur Miguel, Warley, Werverton, João Miguel e Warley C.
- **Vagas:** 3 sem identificação.
- **O que não foi registrado:** nenhum CPF, nenhuma hora trabalhada e nenhuma participação. Antes da PoC, o edital exige a equipe nomeada e a remuneração comprovada (p. 97).

## 8. Perguntas antes de qualquer trabalho contratual

1. A empresa vai disputar o pregão de 11/11? Quem é o responsável legal e quem é o preposto?
2. Há atestados que somem as UST exigidas por tecnologia? Com quais contratantes e datas?
3. A empresa tem CMMI-3/MPS.BR C, ISO 20000, 27001 e 27701, ou só a equivalência com evidência datada externamente?
4. Índices contábeis e patrimônio líquido atendem?
5. Qual preço por UST será ofertado, e sobre qual base: a UST base ou a ajustada?
6. Quem forma a equipe da PoC (humana, sem IA)? Ela conhece Kubernetes, OAuth2, ETL e Prometheus?
7. Os dados dos 3 integrantes faltantes; e se os 7 nomes são definitivos.
8. As 4 soluções do item 15 (ITSM, monitoramento, gestão de projetos e low-code) serão próprias ou de terceiros?

## 9. Próximos passos sugeridos (até 11/11)

| Quando | O quê | Responsável |
|---|---|---|
| hoje | decidir se participa; checar atestados e certificações (seção 4) | gestor da empresa |
| até 10/11 | montar a proposta de preço (Anexo III) e a pasta de habilitação | gestor + G21/G22 |
| 11/11 10h | sessão do pregão | representante legal |
| após habilitação | treinar a equipe para a PoC: roteiro de 5 dias, sem IA | equipe técnica |
| após homologação | catálogo pactuado → OS autorizadas → aí sim, produção pela fábrica | fábrica + gestor |

> Nada aqui é medição nem aceite. O laboratório não gera UST contratual. A meta de 60.000 UST do pacote é só uma meta de teste.
