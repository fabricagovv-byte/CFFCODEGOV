# Arquitetura — MOD-003 Upload de PDF

Arquivos fora do banco em UPLOAD_DIR/AAAA/MM/<uuid>.pdf; tabela arquivos com sha256 e tamanho. Leitura em blocos de 1 MB; arquivo parcial removido em qualquer falha.

Visão geral: `projetos/gestao-documental/docs/ARQUITETURA.md`.
