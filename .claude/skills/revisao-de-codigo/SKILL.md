---
name: revisao-de-codigo
description: Use ao concluir tarefa/módulo ou antes de integrar (pedir revisão) e ao receber comentários de revisão (avaliar com rigor técnico, sem concordar por educação nem aplicar às cegas).
---
# Revisão de código — pedir e receber

Adaptado de superpowers/requesting-code-review e receiving-code-review (MIT) — originais em `fabrica/conhecimento/superpowers/`.

**Pedir:** depois de cada tarefa relevante e antes de integrar. Entregue ao revisor (G13/E18 ou `/code-review`): o que foi feito, requisitos (IDs do edital), faixa de commits (`git diff BASE..HEAD`), como testar. Corrija críticos antes de seguir; registre em `REVISOES.md`.

**Receber:** para cada item — entenda (pergunte se não estiver claro), **verifique no código** se procede, avalie (procede / não procede / é YAGNI), responda com fato técnico, implemente na ordem: bloqueantes → simples → complexos, testando cada um. Discorde com evidência quando o revisor estiver errado. Nada de "ótima observação!" sem verificar.
