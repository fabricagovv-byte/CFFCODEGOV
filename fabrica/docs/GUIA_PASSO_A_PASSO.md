# Passo a passo — do começo ao fim

## A. Uma vez só (configuração)

Para cada sistema novo, crie um repositório a partir do modelo — ver [COMO_INICIAR.md](COMO_INICIAR.md) e [PADRAO_REPOSITORIOS.md](PADRAO_REPOSITORIOS.md).


1. Abra o repositório no Claude Code (app, web ou terminal) ou no Codex.
2. Diga **"INICIAR FÁBRICA"**. Isso roda `fabrica.py agentes gerar` + `fabrica.py iniciar` e mostra o que está OK/pendente.
3. Se usar skills externas próprias, envie-as e diga onde estão. A fábrica não instala skills sozinha.

## B. Para cada contrato

| Passo | Você faz | A fábrica faz | Resultado |
|---|---|---|---|
| 1 | Envia edital, TR, contrato, OS, tabela | G02 lê tudo, cria `contratos/<ID>/` | matriz de rastreabilidade |
| 2 | Responde aos campos faltantes | `contrato faltantes` | `contrato.yaml` completo |
| 3 | Preenche `PROFISSIONAIS.csv` | G18 confere com as exigências do edital | equipe registrada |
| 4 | Diz "PLANEJAR CONTRATO" | G04 gera GEC; E02 cria tarefas | `GEC.md`, quadro de tarefas |
| 5 | **Aprova o GEC e autoriza a OS** | — | `autorizado: true` na OS |
| 6 | Diz "EXECUTAR OS" | 15 passos por módulo: código, testes, revisão, segurança, commits | código + evidências |
| 7 | Profissionais revisam/aprovam e registram em `PARTICIPACOES.csv` | G17 audita | pendências humanas resolvidas |
| 8 | — | "RELATÓRIO DIÁRIO" todo dia | `relatorios/diarios/` |
| 9 | Fim do mês: "MEDIR PRODUÇÃO" + "GERAR RELATÓRIO mensal" | G15 mede; G19 relata | memória de cálculo |
| 10 | "PREPARAR ENTREGA" | checklist 100 + pacote ZIP | `ENTREGA_<C>_<OS>.zip` |
| 11 | Envia ao fiscal; recebe o termo | registra `ACEITE.md` | "aceito" na medição |
| 12 | "PREPARAR PUBLICAÇÃO" → autoriza → "PUBLICAR PRODUÇÃO" | G11 publica com backup e rollback | sistema no ar |

## C. Comandos da CLI mais usados

```bash
F="python3 fabrica/ferramentas/fabrica.py"
$F iniciar                                   # verifica tudo
$F painel                                    # visão do diretor
$F contrato novo PMX-2026-01                 # novo contrato
$F contrato faltantes PMX-2026-01            # o que falta no formulário
$F tarefas criar --agente G06 --descricao "API de login" --contrato PMX-2026-01 --os OS-01 --modulo MOD-001 --arquivo backend/app/routers/auth.py
$F tarefas mover T-0001 READY --por G14
$F tarefas listar --status BLOCKED
$F msg --de G06 --para G13 --tarefa T-0001 --texto "Pronto para revisão"
$F bloqueio --por G11 --tarefa T-0009 --texto "Sem acesso ao servidor de homologação"
$F evidencias preparar PMX-2026-01 OS-01
$F testes executar PMX-2026-01 OS-01
$F evidencias commits PMX-2026-01 OS-01
$F auditar PMX-2026-01 OS-01
$F medir PMX-2026-01 OS-01
$F checklist PMX-2026-01 OS-01
$F relatorio diario PMX-2026-01
$F relatorio mensal PMX-2026-01 --data 2026-11-01
$F relatorio profissional PMX-2026-01 --profissional P02 --data 2026-11-01
$F entrega PMX-2026-01 OS-01
$F producao estatisticas PRODUCAO_HISTORICA.csv
$F planilha gerar PLANILHA_PREENCHIMENTO.xlsx            # modelo para preencher
$F planilha importar PMX-2026-01 PLANILHA_PREENCHIMENTO.xlsx
$F profissionais importar PMX-2026-01 equipe.csv          # nome, função, CPF (CPF fica fora do git)
$F profissionais oficial PMX-2026-01                      # lista com CPF completo (pasta privada)
$F rateio semanal PMX-2026-01 --data 2026-11-02 --total 250
$F relatorio semanal PMX-2026-01 --data 2026-11-02        # inclui o rateio
$F stacks listar                                          # linguagens disponíveis
$F repositorio novo ../pmx-001-sgd --id PMX-001-SGD --sistema "Gestão Documental" --componente backend=java-spring --componente frontend=react-vite
$F repositorio lote PLANILHA_PREENCHIMENTO.xlsx ../repos  # um repositório por linha da aba PROJETOS
$F projeto verificar --instalar                           # testa os componentes do PROJETO.yaml
$F portfolio ../repos/* --saida PORTFOLIO.md              # soma de todos os repositórios
$F pacotes ./saida                                        # gera CONFIGURACAO_FABRICA.zip e PREENCHIMENTO.zip
```

## D. Produção automática diária

Skill `producao-diaria`. Para agendar: no Claude Code, peça "agende a produção diária às 18h" (Routines) ou use `/loop`;
num servidor, `cron` com `claude -p "/producao-diaria"`. Exige credenciais e permissões configuradas por você.
OS sem autorização: a rotina só planeja.

## E. Papéis humanos × agentes

- Agentes executam, verificam e documentam.
- Profissionais reais conduzem, orientam, revisam, corrigem e **aprovam**; a responsabilidade técnica é deles.
- Um gerente de projeto humano não precisa fazer tudo: G01/G03/G04/G14/G19 cuidam de quadro, prazos, relatórios e medição; o gerente decide, aprova e fala com o órgão.
