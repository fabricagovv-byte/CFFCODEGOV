# IA gratuita na fábrica — FreeLLMAPI

**O que é:** um servidor local que junta as cotas gratuitas de vários provedores de IA (Google, Groq, Mistral, OpenRouter,
Cerebras, Kilo, Pollinations, OVH e outros) atrás de **um único endereço**, compatível com OpenAI (`/v1/chat/completions`,
`/v1/responses`) e com Anthropic (`/v1/messages`). Um roteador escolhe o melhor modelo livre e troca de provedor quando um
esgota a cota. As chaves ficam criptografadas (AES-256-GCM) num SQLite local.

- Origem: pacote `Free-LLM-API-main.zip` enviado pelo usuário em 08/11/2026 (projeto `tashfeenahmed/freellmapi`, versão 0.2.1).
- Licença: MIT (ver `codigo/LICENSE`). O app de desktop e as imagens do README não foram copiados.
- Código: `codigo/` (sem alterações). Testes do próprio projeto em 08/11/2026: **1.022 de 1.024 passaram**; os 2 que falharam
  (`analytics-requests.test.ts`) usam datas fixas de julho de 2026 com janela de "últimos 7 dias" e expiraram com o calendário —
  não é defeito do programa.

## Ligar, parar, ver

```bash
bash fabrica/integracoes/freellmapi/iniciar.sh          # instala (1ª vez), compila, sobe em 127.0.0.1:3001 e cria a conta
bash fabrica/integracoes/freellmapi/iniciar.sh status
bash fabrica/integracoes/freellmapi/iniciar.sh parar
```

Requer Node.js 20+. Dados, chave de criptografia, senha do painel e chave unificada ficam **fora do git**, em
`~/.fabrica/freellmapi/` (permissão 600). Painel: `http://127.0.0.1:3001` (login `admin@fabrica.local`, senha no arquivo
`senha_painel`). O script já ativa os 4 provedores que funcionam **sem chave** (Kilo, Pollinations, OVH, AI Horde) — com
limites baixos (uma pergunta por vez, poucas por minuto).

## Usar

**Na fábrica:**

```bash
python3 fabrica/ferramentas/fabrica.py ia status
python3 fabrica/ferramentas/fabrica.py ia perguntar "Explique em 3 linhas o que é glosa por SLA"
python3 fabrica/ferramentas/fabrica.py ia perguntar "Resuma este texto público:" --arquivo caminho/arquivo.md
```

O comando **recusa** texto com CPF, CNPJ, e-mail ou telefone e qualquer arquivo de pasta `privado/` ou `.env`.
Cada uso fica registrado em `fabrica/comunicacao/IA_USO.jsonl` (data, modelo, tokens e o hash do pedido — **sem o conteúdo**).

**Em outros programas, na sua máquina:**

| Programa | Configuração |
|---|---|
| SDK OpenAI, LangChain, apps | `base_url = http://127.0.0.1:3001/v1`, chave = conteúdo de `~/.fabrica/freellmapi/chave_unificada` |
| Codex CLI | provedor em `~/.codex/config.toml` com `base_url = "http://127.0.0.1:3001/v1"` e `env_key` apontando para a chave unificada |
| Claude Code | `ANTHROPIC_BASE_URL=http://127.0.0.1:3001` e `ANTHROPIC_AUTH_TOKEN=<chave unificada>` (não use `ANTHROPIC_API_KEY`) |

Modelos gratuitos são bem mais fracos que os pagos: servem para rascunho, dúvidas e tarefas simples, não para conduzir os 44 agentes.

## Mais capacidade (chaves gratuitas, sem cartão)

Crie conta e gere a chave em Groq, Google AI Studio, Mistral, OpenRouter e Cerebras; cadastre no painel (página **Keys**).
Numa sessão na nuvem do Claude Code, cada provedor também precisa estar liberado na rede do ambiente (hoje estão liberados
só `api.kilo.ai`, `text.pollinations.ai`, `oai.endpoints.kepler.ai.cloud.ovh.net`, `oai.aihorde.net` e `api.freellmapi.co`).

## Regras de uso (obrigatórias)

1. **Só dados públicos ou fictícios.** Nunca CPF, dados de cidadãos, documentos sigilosos do órgão ou segredos: provedores
   gratuitos podem guardar e usar o que recebem (LGPD; regras 6 e 9 do AGENTS.md).
2. **Não é para produção nem para sistemas entregues ao órgão.** Os próprios termos dizem "experimentação, não produção"
   (NVIDIA e GitHub Models: só avaliação; Cohere: evitar). Para IA dentro de um sistema contratado, use API paga com contrato.
3. **Resposta de IA é rascunho**, não registro de trabalho, revisão, medição nem aceite (regra 1). Confira antes de usar.
4. **Prova de conceito do PE 223/2026 (Paraná): IA generativa é proibida** (edital p. 93, item 24.2.8; p. 120, item 8.3).
5. **Não compartilhe o endereço** com outras pessoas e não exponha a porta fora de `127.0.0.1` (o servidor é de um usuário só).
