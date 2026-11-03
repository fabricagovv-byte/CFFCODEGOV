# Planejamento de Projeto Sustentável (PPJ) — TESTE-002

Gerado em 2026-11-03T01:05:11-03:00 pelo Planejador GEC (G04). Itens **a preencher** dependem de informação do contrato ou da equipe.

## 1. Identificação

- Órgão: Órgão Fictício de Demonstração
- Contrato: TESTE-002 · Processo: **a preencher** · Edital: **a preencher**
- Objeto: Atendimento ao cidadão e protocolo (demonstração da fábrica — FICTÍCIO)
- Vigência: 2026-11-03 a 2027-03-31

## 2. Objetivo e escopo

Executar o objeto contratado com entregas verificáveis por ordem de serviço. OS registradas: OS-TESTE-002 (Projeto ATENDIMENTO — interessados e protocolos).

## 3. Entregas e módulos

- OS-TESTE-002/MOD-100 Base modular para cadastros — área BACKEND, previsto — UST
- OS-TESTE-002/MOD-101 Cadastro de interessados — área BACKEND, previsto — UST
- OS-TESTE-002/MOD-102 Cadastro de protocolos — área BACKEND, previsto — UST

## 4. Equipe

- **a preencher** (informe nomes e funções)

## 5. Capacidade, saldo e cronograma

- Contratado: 300.0 UST · Aceito: 0 · Comprovado: 80.4 · Saldo oficial: 300.0
- Média diária informada: sem histórico · Projeção de esgotamento: sem histórico dias
- Marcos e datas: ver GEC.md, seção 8.

## 6. Sustentação (continuidade do serviço)

- Manutenção corretiva, adaptativa e evolutiva por OS, com testes de regressão automatizados no CI.
- Monitoramento de saúde (/api/health), backup diário com teste de restauração mensal e plano de recuperação (PLANO_CONTINUIDADE.md).
- Documentação viva (manuais de publicação e operação) e transferência de conhecimento ao fim do contrato (código, migrações, imagens, último backup, histórico de commits).
- Níveis de serviço do contrato: **a preencher**

## 7. Sustentabilidade

Base: Lei 14.133/2021 (desenvolvimento nacional sustentável como princípio e objetivo da contratação) e critérios do edital. Confirmar no texto vigente e no Guia Nacional de Contratações Sustentáveis aplicável.

| Dimensão | Prática no projeto | Evidência |
|---|---|---|
| Ambiental | Processos 100% digitais (sem papel), infraestrutura em contêineres dimensionada à demanda, desligamento de ambientes ociosos | Docker Compose, manuais digitais |
| Ambiental | Reuso de componentes e builds otimizados (menos processamento e tráfego) | build do frontend, cache de estáticos |
| Social | Acessibilidade digital (WCAG/eMAG), proteção de dados (LGPD), capacitação da equipe e do órgão | testes de interface, SEGURANCA_LGPD.md |
| Econômica | Software livre, sem aprisionamento a fornecedor; código e dados entregues ao órgão; medição transparente | pacote de entrega, memória de cálculo |
| Governança | Rastreabilidade (commits, testes, auditoria), revisão humana, relatórios diários | evidências por módulo, fechamentos |

## 8. Riscos

- Ver GEC.md (seção 10) e AGENT_BLOCKERS.md.

## 9. Indicadores

- Saldo e consumo do contrato (fechamento diário).
- Taxa de testes aprovados e defeitos reabertos.
- Tempo de atendimento das OS e cumprimento de SLA.
- Pendências de aceite do órgão.

---
Aprovação humana: **pendente**.
