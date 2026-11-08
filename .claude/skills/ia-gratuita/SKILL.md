---
name: ia-gratuita
description: IA GRATUITA / FREELLMAPI / USAR IA DE GRAÇA — liga o FreeLLMAPI (cotas gratuitas de vários provedores atrás de um endereço compatível com OpenAI e Anthropic) e faz perguntas pela fábrica, bloqueando dados pessoais e arquivos privados e registrando o uso sem o conteúdo.
---
# IA GRATUITA (FreeLLMAPI)

1. Ligar: `bash fabrica/integracoes/freellmapi/iniciar.sh` (status | parar). Guia: `fabrica/integracoes/freellmapi/LEIA-ME.md`.
2. Testar: `python3 fabrica/ferramentas/fabrica.py ia status`.
3. Perguntar: `python3 fabrica/ferramentas/fabrica.py ia perguntar "<texto>" [--arquivo F] [--modelo M]`.
4. Nunca envie CPF, dados de cidadãos, documentos sigilosos ou segredos; o comando recusa CPF/CNPJ/e-mail/telefone e `privado/`.
5. Resposta é rascunho: não vira registro, medição, revisão nem aceite. Não use em sistema entregue ao órgão nem na PoC do PE-223.
6. Sem resposta: provedores anônimos têm cota baixa; espere ~1 min ou cadastre chaves gratuitas no painel (e libere o host na rede do ambiente de nuvem).
