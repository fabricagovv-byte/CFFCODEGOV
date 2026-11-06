# Escopo — MOD-002 Correções de validação e privacidade (M03, M05, M07, M08)

- Contrato: FIC-COM-2026-001 · OS: OS-FIC-002
- Item contratual: CORRETIVA-SEM-ITEM · Previsto: 0

## Descrição
Corrige defeitos do código que veio no pacote (achados 3, 4, 5, 10, 11 e 12). Não cria item novo de escopo do TR; por isso não é medido (ver MEDICAO.md).

## Funcionalidades
- Leitor (VIEWER) vê só publicações PUBLICADAS, na lista e no contador (achado 3; critério de aceite do M03).
- Chamado com contato inexistente responde 404 em vez de erro 500 (achado 4).
- Exportação CSV neutraliza células que começam com = + - @ (achado 5).
- Campanha com canal inexistente responde 404, e o banco passou a ter chave estrangeira (achado 10).
- E-mail do contato validado (achado 11).
- Leitor não recebe descrição nem contato dos chamados (achado 12).
- A tela mostra a mensagem de validação da API em vez de "[object Object]" (defeito encontrado durante os testes de tela).

## Fora do escopo
- Esconder da tela do leitor os formulários e botões que ele não pode usar (o servidor já recusa).
- Finalidade e base legal do consentimento (M07).

Linha de base: o commit `f823f56` é a importação do código original do pacote DIGITALGOV (aparece no git porque os arquivos nasceram nele); não é trabalho desta OS e não é medido.
