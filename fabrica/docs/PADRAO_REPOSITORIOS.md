# Padrão para muitos projetos (ex.: 30 sistemas = 30 repositórios)

## Regras

1. **Um repositório por sistema.** Nome: `<orgao>-<nnn>-<sigla>` em minúsculas (ex.: `pmx-001-sgd`). O mesmo ID, em maiúsculas, vai no `PROJETO.yaml`.
2. **Mesma configuração em todos:** todos nascem do modelo (`CONFIGURACAO_FABRICA.zip` ou `fabrica.py modelo exportar`). O arquivo `fabrica/VERSAO_MODELO` diz de qual versão veio.
3. **Estrutura fixa:** `PROJETO.yaml`, `projetos/<sistema>/<componente>/`, `contratos/<ID>/`, `relatorios/`, `fabrica/`.
4. **Stack declarada:** cada componente aponta para uma stack de `fabrica/stacks/` (ver `fabrica/stacks/VERIFICACAO.md`). O CI testa todos com `fabrica.py projeto verificar --instalar`.
5. **Branches:** `main` protegida (só via PR com CI verde e revisão humana); trabalho em `os-<nnn>-<descricao>`; versões com tag `vX.Y.Z`.
6. **Dados pessoais:** CPF só em `contratos/<ID>/privado/` (fora do git). Nunca commitar `.env`.
7. **Mesma equipe em vários repositórios:** use o mesmo ID de profissional (P01…) em todos para o portfólio somar corretamente.
8. **Visão geral:** `fabrica.py portfolio <repo1> <repo2> ... --saida PORTFOLIO.md` soma medições e rateios de todos.

## Atualizar a configuração em todos os repositórios

Quando a fábrica melhorar, gere o modelo novo e copie para cada repositório **só** `AGENTS.md`, `CLAUDE.md`, `.claude/` e `fabrica/`
(exceto `fabrica/comunicacao/`, que é o histórico do projeto). Depois rode `fabrica.py agentes gerar` e `fabrica.py iniciar`.

## Stacks disponíveis

| Stack | Uso típico |
|---|---|
| python-fastapi | APIs e sistemas administrativos |
| react-vite | interfaces web |
| node-typescript | APIs Node/TypeScript |
| java-spring | sistemas corporativos Java (comum em órgãos federais/estaduais) |
| dotnet-aspnet | ambientes Microsoft |
| php-puro | legados PHP / base para Laravel/Symfony |
| go-http | serviços leves e integrações |
| rust-std | serviços de alto desempenho |

Outra linguagem (Kotlin, Flutter, Angular, Django…): peça "criar stack <nome>"; o agente cria `fabrica/stacks/<id>.yaml` + esqueleto + teste e roda `fabrica.py stacks verificar <id>`.
