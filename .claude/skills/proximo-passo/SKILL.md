---
name: proximo-passo
description: PRÓXIMO PASSO / COMEÇAR / AJUDA / ONDE PAREI — diagnostica o repositório e o contrato do começo ao fim (configuração, documentos, edital, formulário, equipe, documento base, confronto, medição, planejamento, OS, autorização, código testado, medição, abertura/diário/fechamento) e diz ao usuário exatamente o que falta e o que fazer agora. Use no início de toda sessão nova.
---
# PRÓXIMO PASSO (G01 Diretor + G14 Comunicador)

1. `python3 fabrica/ferramentas/fabrica.py agentes gerar >/dev/null && python3 fabrica/ferramentas/fabrica.py iniciar`
2. `python3 fabrica/ferramentas/fabrica.py proximo-passo [<ID-do-contrato>]` (sem ID: usa o único contrato real ou pede para criar um).
3. Responda em no máximo 6 linhas: o que já está pronto (resumo), a **próxima ação** (frase exata para o usuário dizer ou o arquivo a preencher) e, se ajudar, as duas seguintes.
4. Se o usuário pedir, já execute a próxima ação (respeitando autorização de OS e publicação).
5. Treinamento completo: `fabrica/docs/TREINAMENTO.md` (Word no pacote de preenchimento).
