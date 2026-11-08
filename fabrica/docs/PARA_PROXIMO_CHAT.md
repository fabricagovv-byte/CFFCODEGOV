# Para o próximo chat — leia antes de qualquer coisa

Estado em 07/11/2026 (horário de Brasília). Último commit da branch `claude/multiagent-software-engineering-4lvokb`: `acf400a`.
Se o repositório mudou depois disso, confie no `git log` e nos arquivos, não neste texto.

## 1. Primeiros comandos (sempre, nesta ordem)

```bash
python3 fabrica/ferramentas/fabrica.py iniciar          # carrega agentes, skills e regras
python3 fabrica/ferramentas/fabrica.py proximo-passo    # o que falta e a próxima ação
python3 fabrica/continuidade/dg_control.py --root continuidade/DIGITALGOV_WORKSPACE abrir-dia --id DEMO-001
```

Depois diga ao usuário, em poucas linhas: o que está pronto, o que falta e a próxima ação.
Só então execute o pedido dele.

## 2. Onde está cada coisa

| Caminho | O que é |
|---|---|
| `AGENTS.md` | Regras inegociáveis e tabela de comandos (cada comando tem uma skill em `.claude/skills/`). |
| `fabrica/ferramentas/fabrica.py` | CLI da fábrica: contratos, OS, medição, relatórios, participação, IA, sistemas. |
| `contratos/<ID>/` | Um contrato por pasta: `contrato.yaml`, `os/`, `medicoes/`, `relatorios/`, `PLANEJAMENTO.csv`, `PROFISSIONAIS.csv`, `PARTICIPACOES.csv`. |
| `projetos/<nome>/` | Código dos sistemas. `digitalgov-gerenciador` é o gerenciador central (API + painel). |
| `continuidade/DIGITALGOV_WORKSPACE/` | Estado diário por projeto: `PROJETOS/<ID>/` (estado, eventos, diário, handoff) e `CONTROL_CENTER/`. |
| `fabrica/continuidade/dg_control.py` | Comandos de abrir, registrar e fechar o dia, e gerar o kit para outro chat. |
| `fabrica/integracoes/freellmapi/` | IA gratuita local (`LEIA-ME.md`). |
| `fabrica/identidade/papel_timbrado.jpg` | Papel timbrado usado nos Word para o órgão. |
| `fabrica/templates/SISTEMA.yaml` | Formulário para gerar um sistema novo por cadastros. |

## 3. Estado atual

**Contratos**
- `TESTE-001` e `TESTE-002`: demonstração **fictícia**. Nada aqui é contratual.
- `PE-223-2026-PR`: edital do Pregão 223/2026 (Paraná), 223 páginas. Sessão em **11/11/2026, 10h**. Não há OS. A prova de conceito proíbe IA generativa (p. 93 e 120). Equipe com 7 nomes, 3 vagas.
- `FIC-COM-2026-001`: minuta. O órgão **ainda não foi informado**. Há 202,5 UST executadas no MOD-001, com medição parcial e catálogo ainda **não ratificado** pelo órgão (R$ 30,00/UST). Aceito = 0, pago = 0. Nenhuma quantidade é considerada aceita sem OS assinada pelo órgão.

**Gerenciador central** (`projetos/digitalgov-gerenciador`)
- API com 42 testes passando no PostgreSQL. Painel web somente leitura em `/`.
- Primeiro administrador criado, login `admin`. A senha está em `/root/.fabrica/gerenciador/senha_admin`, fora do repositório. Não a mostre no chat.
- Banco `digitalgov_gerenciador` existe no PostgreSQL local deste ambiente. Ele não é um banco central persistente.
- Para subir (se estiver parado): `pg_ctlcluster 16 main start`, depois `uvicorn app.main:app` na pasta `backend` com `GERENCIADOR_DATABASE_URL` (ver `projetos/digitalgov-gerenciador/README.md`).
- Limites: sem telas de cadastro, sem lançamento de horas pela tela (só pela API), sem conector de agentes, sem implantação no órgão.

**Continuidade**
- `DEMO-001`: projeto fictício em ESCOPAR, com um dia fechado e o kit de handoff. Horas e UST = zero.
- Existe uma rotina agendada que gera o relatório técnico às 16h46 em dias úteis. Ela não faz o fechamento do dia.

**IA gratuita**
- `fabrica.py ia status` / `ia perguntar`. Precisa do serviço no ar: `bash fabrica/integracoes/freellmapi/iniciar.sh`.
- Só dados públicos ou fictícios. Recusa CPF, CNPJ, e-mail e telefone.

## 4. Pendências que dependem do usuário

1. **ESCOPAR de um projeto real** (gate E0 do prompt V3.1): qual sistema será desenvolvido? Sem isso, não se abre projeto.
2. **Qual contrato ou OS vale?** `FIC-COM-2026-001` é o único com trabalho medido, mas é uma minuta. Confirmar.
3. **Edital e contrato** do órgão, quando existirem. O `PROMPT_MESTRE_EDITAIS.md` citado em conversas anteriores **nunca chegou**.
4. **Banco persistente do gerenciador** (servidor do usuário, não este ambiente).
5. **Fechamento automático às 18h**: não configurado. Só com autorização expressa.
6. **Linguagem dos próximos sistemas** (Java ou Python/React): pergunta em aberto.
7. **Horas humanas**: o usuário lança. A IA não lança e não converte tempo de agente em hora de pessoa.

## 5. Regras que não podem ser quebradas

- Nada inventado: sem registro = "sem registro". Não invente horas, UST, aceite, teste, commit ou link.
- Planejado, iniciado, executado, verificado e aceito são coisas diferentes. Aceite exige documento do órgão.
- Não execute OS sem `autorizacao.autorizado: true` + `autorizado_por` + `data`.
- UST ≠ PF ≠ horas. Só converte com a fórmula escrita no contrato.
- CPF completo só em `contratos/<ID>/privado/` (no `.gitignore`). Nunca em arquivo versionado.
- Senhas, chaves e `.env` nunca entram no git.
- Resposta de IA é rascunho, não registro de trabalho.
- Não publique nada, não envie nada ao órgão e não crie PR sem pedido explícito.
- Prova de conceito do PE-223: IA generativa proibida.
- Antes de dizer "passou", rode o comando e leia a saída, com o código de saída real (não use `| tail` para esconder falha).

## 6. Como abrir, continuar e fechar um dia

```bash
# Abrir: resumo do último estado e do último handoff
python3 fabrica/continuidade/dg_control.py --root continuidade/DIGITALGOV_WORKSPACE abrir-dia --id <ID>

# Durante: registrar só o que aconteceu de fato (ENTREGA exige arquivo de evidência)
python3 fabrica/continuidade/dg_control.py --root continuidade/DIGITALGOV_WORKSPACE registrar --id <ID> \
  --tipo NOTA --descricao "..." --proximo "..."

# Fechar: relatório do dia, consolidado e handoff; depois o kit para outro chat
python3 fabrica/continuidade/dg_control.py --root continuidade/DIGITALGOV_WORKSPACE fechar-dia --id TODOS
python3 fabrica/continuidade/dg_control.py --root continuidade/DIGITALGOV_WORKSPACE kit-handoff --id <ID>

# Guardar o estado no git (a sessão é descartável)
git add continuidade && git commit -m "continuidade: fechamento de <data>" && git push
```

## 7. Mapa de pedidos comuns

| Pedido do usuário | O que fazer |
|---|---|
| "Relatório técnico" / "medição do dia" | `fabrica.py relatorio tecnico <C>`. Entregar o `.docx`. |
| "Participação da equipe" | `fabrica.py participacao modelo <C>`. Entregar o Word. Depois de preenchido: `participacao importar`. |
| "Quanto cada um fez" | Só com o que o usuário registrou. A divisão das UST segue o peso do tipo × senioridade. |
| "Gerar sistema" | Formulário `fabrica/templates/SISTEMA.yaml` → `fabrica.py sistema gerar` e `sistema preview`. |
| "Pergunta para a IA" | `fabrica.py ia perguntar "..."` (sem dados pessoais). |
| "Abrir projeto novo" | Só depois de ESCOPAR aprovado pelo usuário: `continuidade ... novo-projeto`. |
| "Começar a executar" | Só com OS autorizada. Sem ela, responder que não há autorização. |

## 8. Fim de sessão

1. `fechar-dia` e `kit-handoff` do que foi trabalhado.
2. `fabrica.py tarefas validar` e os testes dos módulos mexidos (com o código de saída).
3. `git status`: não pode aparecer `.env`, senha, chave, `node_modules`, banco ou `privado/`.
4. Commit com os trailers do sistema e `git push -u origin claude/multiagent-software-engineering-4lvokb`.

## 9. Texto para colar em um chat novo

```
Você está no repositório CFFCODEGOV (Fábrica Digitalgov). Leia fabrica/docs/PARA_PROXIMO_CHAT.md e AGENTS.md.
Rode fabrica.py iniciar e fabrica.py proximo-passo, depois abrir-dia do projeto relevante.
Diga em poucas linhas o que está pronto, o que falta e a próxima ação. Em português, de forma simples.
Não invente horas, UST, aceite, teste ou commit. Meu pedido agora: <escreva aqui>
```
