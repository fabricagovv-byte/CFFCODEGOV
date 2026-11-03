# Como me colocar para trabalhar (Claude Code ou Codex)

## 1. Criar o repositório do sistema (um por sistema)

**Opção A — pelo ZIP de configuração (mais simples):**
1. Descompacte `CONFIGURACAO_FABRICA.zip` → pasta `fabrica-modelo/`.
2. Renomeie para o ID do projeto (ex.: `pmx-001-sgd`) e suba como repositório novo no GitHub (privado).

**Opção B — eu crio (com a CLI):**
```bash
python3 fabrica/ferramentas/fabrica.py repositorio novo ../pmx-001-sgd \
  --id PMX-001-SGD --sistema "Gestão Documental" --orgao "Prefeitura X" --contrato CT-12-2026 \
  --componente backend=python-fastapi --componente frontend=react-vite
```
**Opção C — vários de uma vez (até 30+):** preencha a aba PROJETOS da planilha e rode
`python3 fabrica/ferramentas/fabrica.py repositorio lote PLANILHA_PREENCHIMENTO.xlsx ../repos`.

**Opção D — GitHub "Template repository":** suba o modelo uma vez, marque *Settings → Template repository* e use *Use this template* para cada sistema novo.

## 2. Abrir a sessão

- **Claude Code no celular/web (claude.ai/code):** nova sessão → escolha o repositório → escreva os comandos abaixo.
- **Claude Code no computador:** `cd pmx-001-sgd && claude`.
- **Codex:** abra o repositório; ele lê o `AGENTS.md` automaticamente.

## 3. Mensagens para colar (na ordem)

1. `INICIAR FÁBRICA`
2. Anexe a planilha preenchida e os PDFs → `IMPORTAR PLANILHA CT-12-2026` e depois `NOVO CONTRATO CT-12-2026`
3. Responda às perguntas do que faltar.
4. `PLANEJAR CONTRATO CT-12-2026`
5. Aprove o plano e escreva no YAML da OS (ou na conversa) quem autorizou e quando → `EXECUTAR OS OS-001`
6. Todo dia: `RELATÓRIO DIÁRIO CT-12-2026`
7. Toda semana: informe o total (ex.: "a semana de 02/11 fechou 250 UST") → `RATEIO SEMANAL CT-12-2026`
8. Todo mês: `MEDIR PRODUÇÃO` → `GERAR RELATÓRIO mensal` → `PREPARAR ENTREGA`
9. Publicar: `PREPARAR PUBLICAÇÃO` → autorização → `PUBLICAR PRODUÇÃO`

## 4. Como você recebe o código

| Forma | Como | Quando usar |
|---|---|---|
| Repositório Git | cada commit/push fica no GitHub; baixe com `git clone` ou "Download ZIP" | sempre (é a fonte oficial) |
| Pacote de entrega | `PREPARAR ENTREGA` gera `ENTREGA_<contrato>_<OS>.zip` (código, banco, infra, testes, evidências, medição, relatórios, manifesto SHA-256) | entrega mensal / por OS ao órgão |
| Versão marcada | `git tag v1.0.0 && git push --tags` (ou Release no GitHub) | homologação e produção |

## 5. O que eu (IA) faço e o que só vocês fazem

- **Eu:** leio documentos, planejo, programo, testo, reviso, documento, registro evidências, meço, gero relatórios e pacotes.
- **Vocês:** designam a equipe, autorizam a OS, revisam/corrigem/aprovam, informam totais aceitos, respondem ao órgão, autorizam publicação.
- Sem registro de vocês, os relatórios mostram "sem registro" — nunca invento participação, assinatura ou aceite.
