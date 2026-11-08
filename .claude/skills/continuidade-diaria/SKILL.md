---
name: continuidade-diaria
description: ABRIR DIA / FECHAR DIA / CONTINUAR PROJETO / RETOMAR CHAT / KIT DE HANDOFF — abre o dia de um projeto lendo o estado persistido, registra eventos reais, fecha o dia (relatório diário, consolidado e handoff) e gera o ZIP para retomar em outro chat. Nunca lança horas nem UST.
---
# CONTINUIDADE DIÁRIA (E.P.D.A. ampliado, V3.1)

Workspace persistido no repositório: `continuidade/DIGITALGOV_WORKSPACE` (utilitário `fabrica/continuidade/dg_control.py`).

1. **Antes de qualquer trabalho no dia** — abrir:
   `python3 fabrica/continuidade/dg_control.py --root continuidade/DIGITALGOV_WORKSPACE abrir-dia --id <ID>`
   Mostra o estado, o último passo, as pendências, os últimos eventos e o último handoff. Continue do último passo válido.
2. **Durante o dia** — registrar cada ação real:
   `... registrar --id <ID> --tipo NOTA|ENTREGA --descricao "..." --proximo "..." [--evidencia arquivo]`
   Entrega exige arquivo de evidência existente (o hash SHA-256 é gravado). Nenhum registro aceita ou mede.
3. **Fim do dia** — fechar e gerar o ZIP de continuidade:
   `... fechar-dia --id TODOS` (relatório consolidado) e `... kit-handoff --id <ID>` (ZIP para outro chat).
   Depois: `git add continuidade && git commit && git push`, para o estado sobreviver à sessão.
4. **Novo projeto** — só depois de o usuário definir o sistema e enviar o contrato/OS:
   `... novo-projeto --id <ID> --nome "..." --contrato <C> --tipo DESENVOLVIMENTO|MANUTENCAO|SUSTENTACAO|SUPORTE|CONSULTORIA|MISTO`
   Nasce em ESCOPAR/PENDENTE. Não há horas, UST nem aceite automáticos.
5. Horas humanas são lançadas pelo usuário no gerenciador (`projetos/digitalgov-gerenciador`); aqui só se registra o que aconteceu.
