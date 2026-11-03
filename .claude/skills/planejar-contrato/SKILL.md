---
name: planejar-contrato
description: PLANEJAR CONTRATO / PLANEJAR PROJETO — gera o Plano GEC, cronograma, EAP, RACI, módulos, riscos e cria as tarefas no quadro distribuídas entre os agentes. Use depois do formulário do contrato preenchido.
---
# PLANEJAR CONTRATO (G04 Planejador GEC, G05 Arquiteto, E02 Tech Lead, G14 Comunicador)

1. Confira `python3 fabrica/ferramentas/fabrica.py contrato faltantes <ID>`; campos críticos faltando (OS, medição, equipe) → pare e peça ao usuário.
2. Preencha `contratos/<ID>/GEC.md` seguindo todas as seções do modelo. Para cada módulo: ID, nome, funcionalidades, requisitos (IDs da matriz), tecnologias, profissional responsável (de PROFISSIONAIS.csv, ou "A CADASTRAR"), agentes, prazo, dependências, medição prevista (item da tabela), testes, evidências, critério de aceite.
3. Crie `contratos/<ID>/os/<OS>.yaml` (modelo: contratos/TESTE-001/os/OS-TESTE-001.yaml) com módulos, caminhos de código, comandos de teste e item da tabela. Deixe `autorizacao.autorizado: false` até haver autorização real.
4. Crie as tarefas: `python3 fabrica/ferramentas/fabrica.py tarefas criar --agente <ID> --contrato <ID> --os <OS> --modulo <MOD> --descricao "..." --prioridade ALTA --prazo AAAA-MM-DD --arquivo <caminho> --dep T-000N`.
5. Rode `python3 fabrica/ferramentas/fabrica.py tarefas validar` e apresente o plano para aprovação humana.
