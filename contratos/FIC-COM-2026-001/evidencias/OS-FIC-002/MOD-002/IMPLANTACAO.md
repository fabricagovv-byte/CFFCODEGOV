# Implantação — MOD-002 MOD-002 Correções de validação e privacidade (M03, M05, M07, M08)

Migração `0003_campanha_canal_fk`. Se o banco tiver campanha apontando para canal apagado, a migração para com mensagem e nada é alterado; corrija o dado e rode de novo. Reversão: `python -m app.cli rollback --to 2`.

Não publicado em homologação nem produção (sem autorização de publicação).
