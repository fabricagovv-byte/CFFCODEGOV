---
name: verificar-antes-de-concluir
description: Use ANTES de dizer que algo está pronto, corrigido, passando, entregue ou medido — e antes de commit, push ou relatório. Exige rodar o comando que prova a afirmação nesta mesma resposta e ler a saída. Evidência antes de afirmação, sempre.
---
# Verificar antes de concluir (lei de ferro)

Adaptado de superpowers/verification-before-completion (MIT) — original em `fabrica/conhecimento/superpowers/verification-before-completion/SKILL.md`.

**Nenhuma afirmação de conclusão sem evidência nova.** Se o comando não rodou nesta resposta, você não pode dizer que passa.

1. **Identifique** o comando que prova a afirmação (tabela abaixo).
2. **Rode** o comando completo, agora.
3. **Leia** a saída inteira: código de saída, número de falhas.
4. **Confira**: a saída confirma? Se não, diga a situação real com a evidência.
5. **Só então** afirme — junto com o número (ex.: "29/29 testes passaram").

| Afirmação | Exige | Não basta |
|---|---|---|
| Testes passam | saída do teste com 0 falhas | rodada anterior, "deve passar" |
| Build ok | build com saída 0 | lint ok |
| Bug corrigido | teste do sintoma original passando | "mudei o código" |
| Módulo entregue | `python3 fabrica/ferramentas/fabrica.py auditar` APROVADO + evidências | testes verdes |
| Medição | `python3 fabrica/ferramentas/fabrica.py medir` com memória de cálculo | conta de cabeça |
| Subagente terminou | diff no git + teste rodado por você | relato do subagente |

**Pare** se estiver para escrever "pronto", "perfeito", "deve funcionar" ou para fazer commit sem ter rodado a verificação.
Atenção a encadeamentos com pipe (`pytest | tail`): o código de saída é do `tail`, não do teste. Leia o resultado antes de seguir.
