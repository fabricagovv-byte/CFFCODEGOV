# DIGITALGOV — FÁBRICA CODEX V3 / LABORATÓRIO MULTISSERVIÇOS

Este pacote contém uma **fábrica-base local em Python**: banco central persistente, 15 aplicações demonstrativas reais com CRUD + banco isolado, API do painel, verificação de evidência por hash SHA-256, horas de execução registradas por tarefa, controle de UST em modo laboratório, relatório Word técnico e scripts de teste.

**Não** é uma fábrica autônoma de 100 agentes Codex, nem 15 sistemas governamentais acabados. As posições de agentes são catálogo/configuração; sem infraestrutura remota ou GitHub conectado. **Nenhuma UST contratual foi homologada.**

## Requisitos

- Python 3.10+ (biblioteca padrão para APIs e bancos)
- `pip install -r requirements.txt` para relatórios Word (`python-docx`)

## Iniciar Overview

Na raiz do pacote:

```bash
python manage.py init
python manage.py serve --port 8765
```

Abra **http://127.0.0.1:8765** no mesmo computador. Atualiza a cada cinco segundos consultando SQLite; não inventa progresso.

## Iniciar os 15 projetos demonstrativos

Cada subprojeto tem aplicação real, frontend mínimo + API + SQLite independente, sem autenticação (uso local):

```bash
python projetos/SYS-01/app.py --port 8001
python projetos/SYS-02/app.py --port 8002
# ... até SYS-15 em porta 8015
```

O painel de cada projeto está em `http://127.0.0.1:<porta>`.

## Testes reais

```bash
python scripts/run_all_tests.py
```

O comando testa endpoints de inclusão, consulta, atualização, exclusão, validação e saúde de cada aplicação; grava logs e sumário em `test-results/`. **Passar nos testes não gera UST contratuais.**

## Registrar trabalho e evidências (laboratório)

```bash
python manage.py task-create --os OS-T01 --title "Validar endpoints" --kind AGENTE --actor agente-lab-01 --base 10
python manage.py task-start 1
# Rode os testes reais e gere um arquivo físico de evidência (não invente)
python manage.py task-finish 1 --evidence test-results/SYS-01.txt --test-result PASS
python manage.py task-verify 1 --reviewer "Revisor real" --base 10
python manage.py status
python manage.py report
python manage.py release --project SYS-01
```

`--base` registra hipótese de quantidade, não substitui o catálogo pactuado. `task-verify` é **verificação técnica interna do laboratório**, nunca homologação contratual. Nenhum aceite externo é possível com OS simuladas.

## Relatórios das 18h

Rode manualmente `python manage.py report`, ou configure um agendador **externo** (cron/systemd/Task Scheduler) para executar `python scripts/report_at_18.py` às 18h America/Sao_Paulo; o agendador não está ativo por padrão. O código NÃO mantém sessão Codex aberta e NÃO gera novos projetos sozinho.

## Comandos operacionais

- `python manage.py init` — inicializar banco.
- `python manage.py serve --port 8765` — abrir Overview.
- `python manage.py status` — metas x UST verificadas.
- `python manage.py audit` — verificar trilha de auditoria.
- `python manage.py task-create ...` — cadastrar atividade.
- `python manage.py task-start ID` — início cronológico real.
- `python manage.py task-finish ID ...` — concluir com evidência.
- `python manage.py task-verify ID ...` — revisão técnica interna.
- `python manage.py report` — DOCX analítico com 10 fichas e quadros.
- `python manage.py release --project SYS-01` — ZIP do código de um sistema.

## Integração com GitHub

O código não cria repositórios remotamente sem autenticação. Execute, **após inspeção dos dados**, no diretório desejado:

```bash
git init
git add .
git commit -m "chore: iniciar laboratorio Digitalgov"
git branch -M main
git remote add origin URL_PRIVADA_DO_SEU_REPOSITORIO
git push -u origin main
```

Nunca versione os arquivos SQLite de runtime, senhas, CPFs ou dados reais de clientes; `.gitignore` incluído. Configure CI em GitHub Actions e `secrets`/credenciais no GitHub, não nos documentos.

## Segurança e limites

A API e os 15 CRUDs só escutam em `127.0.0.1`. Não publicar na internet sem autenticação, TLS, backup, revisão de vulnerabilidades e LGPD. O fluxo de UST é separado de horas humanas. **O edital não determina quantas UST valem um CRUD**; depende de catálogo e OS aprovadas. Consulte `docs/COMO_MEDIR_UST_PE223.md`.


## V3 — 15 OPERAÇÕES ESPECIALIZADAS, ALÉM DO CRUD

Esta versão inclui em cada `projetos/SYS-XX/` uma API adicional `POST /api/service/run`, um motor específico `service.py`, tela `/service`, histórico em SQLite e testes de integração. Cada categoria do edital tem lógica própria. Use `python scripts/serve_all.py` para iniciar os 15 servidores de uma vez. Veja `docs/CATALOGO_15_SERVICOS.md` e `docs/COMANDOS_V3.md`.
