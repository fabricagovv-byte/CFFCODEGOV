# COMANDOS E OPERAÇÃO — FÁBRICA V3

## Dependências
Python 3.10+; `pip install -r requirements.txt` somente para Word.

```bash
python manage.py init
python manage.py serve --port 8765
```

Abra http://127.0.0.1:8765 para o painel central e http://127.0.0.1:8765/api/catalog para o catálogo de serviços.

Execute os módulos isolados, cada um em terminal próprio ou usando o lançador:

```bash
python scripts/serve_all.py
```

Módulos operam em 127.0.0.1:8001 até 127.0.0.1:8015. Abra `http://127.0.0.1:8001/service`, e assim por diante. Nenhum acesso à internet é necessário.

Teste todos os serviços:

```bash
python scripts/run_all_tests.py
```

Gerar ZIP para cada módulo:

```bash
python scripts/build_project_zips.py
```

Relatório técnico:

```bash
python manage.py report
```

A fábrica central ainda não implementa execução autônoma de 100 agentes. Para isso o Codex terá de integrar executor autorizado, estado persistente por agente, supervisão, fila, limites de execução, CI e credenciais. Nenhuma UST pode ser inventada ou faturada apenas com demonstrações laboratoriais.
