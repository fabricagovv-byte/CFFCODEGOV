---
name: planejamento-projetos
description: PLANEJAMENTO — o responsável faz o plano (PLANEJAMENTO.csv ou aba PLANEJAMENTO do documento base); a fábrica separa por projeto e calcula UST, horas por perfil, valor, prazo, capacidade da equipe e saldo, cruza com o edital e gera a OS de cada projeto.
---
# PLANEJAMENTO POR PROJETO (G04 Planejador, G02, G03)

1. O plano é do usuário: projeto, módulo, nome, área, serviço do catálogo, quantidade, início, fim, responsável, prioridade. Não invente módulos; sugira e peça confirmação.
2. Leia o edital de novo antes de consolidar: perfis, valor/hora, catálogo de serviços, fórmula de medição e prazos vão para `PERFIS.csv`, `CATALOGO_SERVICOS.csv`, `contrato.yaml medicao.formula` e `EDITAL.yaml prazos` (com cláusula de origem).
3. `python3 fabrica/ferramentas/fabrica.py planejamento consolidar <ID>` → `PLANO_PROJETOS.md` + Word: resumo por projeto, módulos, horas por perfil, capacidade (alerta: perfil sem pessoa ou acima da capacidade), saldo do contrato e prazos.
4. Para cada projeto aprovado: `python3 fabrica/ferramentas/fabrica.py planejamento gerar-os <ID> --projeto <P> --os <OS> --caminho projetos/<sistema>` (sai sem autorização; completar caminhos/testes e registrar quem autorizou).
5. Responda com os alertas primeiro.
