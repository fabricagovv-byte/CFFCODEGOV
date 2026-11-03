# Planejamento de Projeto Sustentável (PPJ) — TESTE-001

Gerado em 2026-11-03T00:28:21-03:00 pelo Planejador GEC (G04). Itens **a preencher** dependem de informação do contrato ou da equipe.

## 1. Identificação

- Órgão: Órgão Fictício de Demonstração
- Contrato: TESTE-001 · Processo: não se aplica (fictício) · Edital: não se aplica (fictício)
- Objeto: Desenvolvimento de sistema de Gestão Documental Pública (demonstração da fábrica)
- Vigência: 2026-11-03 a 2026-12-31

## 2. Objetivo e escopo

Executar o objeto contratado com entregas verificáveis por ordem de serviço. OS registradas: OS-TESTE-001 (Gestão Documental Pública).

## 3. Entregas e módulos

- OS-TESTE-001/MOD-001 Autenticação e controle de acesso — área —, previsto 2 UST
- OS-TESTE-001/MOD-002 Cadastro documental — área —, previsto 2 UST
- OS-TESTE-001/MOD-003 Upload de PDF — área —, previsto 2 UST
- OS-TESTE-001/MOD-004 Pesquisa — área —, previsto 1 UST
- OS-TESTE-001/MOD-005 Painel administrativo — área —, previsto 1 UST
- OS-TESTE-001/MOD-006 Auditoria — área —, previsto 1 UST
- OS-TESTE-001/MOD-007 Infraestrutura e documentação — área —, previsto 1 UST

## 4. Equipe

- **a preencher** (informe nomes e funções)

## 5. Capacidade, saldo e cronograma

- Contratado: 10.0 UST · Aceito: 0 · Comprovado: 10 · Saldo oficial: 10.0
- Média diária informada: sem histórico · Projeção de esgotamento: sem histórico dias
- Marcos e datas: ver GEC.md, seção 8.

## 6. Sustentação (continuidade do serviço)

- Manutenção corretiva, adaptativa e evolutiva por OS, com testes de regressão automatizados no CI.
- Monitoramento de saúde (/api/health), backup diário com teste de restauração mensal e plano de recuperação (PLANO_CONTINUIDADE.md).
- Documentação viva (manuais de publicação e operação) e transferência de conhecimento ao fim do contrato (código, migrações, imagens, último backup, histórico de commits).
- Níveis de serviço do contrato: não se aplica (fictício)

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
