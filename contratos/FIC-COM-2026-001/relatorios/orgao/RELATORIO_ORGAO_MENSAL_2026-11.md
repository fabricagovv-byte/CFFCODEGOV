# Relatório mensal de medição — novembro de 2026

**Órgão:** [nome do órgão]

**Contrato:** [número do contrato]

**Objeto:** Plataforma Integrada de Comunicação Institucional e Atendimento Digital

**Contratada:** V4 Tecnologia Brasil · DigitalGov

**Período:** novembro de 2026

Encaminhamos a medição dos serviços executados no período, para conferência e aceite.

## Serviços executados

| Ordem de serviço | Onde estão as UST (módulo e entrega do contrato) | UST | Valor (UST × R$ 30,00) |
|---|---|---|---|
| OS-FIC-002 | M01 Identidade e segurança de acesso — entrega 2 de 4: Controle de sessão | 202,5 | R$ 6.075,00 |
| **Total** | | **202,5** | **R$ 6.075,00** |

## Como as UST foram calculadas

- **M01 Identidade e segurança de acesso:** 270 UST base × fator 3 = 810 UST. O módulo tem 4 entregas: 810 ÷ 4 entregas = 202,5 UST por entrega. Entregue: entrega 2, Controle de sessão = 202,5 UST × R$ 30,00 = R$ 6.075,00.

## O que foi entregue

### M01 Identidade e segurança de acesso — entrega 2 de 4: Controle de sessão

- **Banco de dados:** Tabela de sessões (sessions): cada acesso com validade de 8 horas e data de encerramento; Tabela de tentativas de acesso (login_attempts), com índices por usuário e por IP; Migração 0002 com reversão.
- **Back-end:** Login cria a sessão no servidor (POST /api/login); Saída encerra a sessão no servidor (POST /api/logout); Toda rota protegida confere se a sessão existe, não foi encerrada e não venceu; Bloqueio após 5 senhas erradas em 15 minutos por usuário (20 por IP); Registro de acesso, falha, bloqueio e saída na auditoria.
- **Front-end:** Botão Sair encerra a sessão no servidor; Mensagem de bloqueio na tela de acesso.

## Perfis e horas

Horas trabalhadas em cada perfil, preenchidas pela contratada.

| Item | Perfil | Horas |
|---|---|---|
| MOD-001 | Programador Sênior — Banco de dados |  |
| MOD-001 | Programador Sênior — Back-end |  |
| MOD-001 | Programador Sênior — Front-end |  |
| MOD-001 | Programador Sênior — Testes |  |

## Situação do contrato

| Contratado (UST) | Executado até o período (UST) | Saldo (UST) |
|---|---|---|
| 12.000 | 202,5 | 11.797,5 |

## Regra de medição do contrato

Cada módulo do contrato é pago pelas suas entregas. Uma entrega só é medida quando está completa, com o que a última coluna indica (em geral banco de dados, back-end e front-end funcionando). Para receber o módulo inteiro, todas as entregas do módulo precisam ser feitas: se o módulo tem 6 entregas, são as 6. Quando a divisão não é exata, o valor é arredondado em centésimos e a última entrega do módulo fecha o total.

| Módulo | UST do módulo | Nº de entregas | Entregas | UST por entrega | Cada entrega exige |
|---|---|---|---|---|---|
| M01 Identidade e segurança de acesso | 810 | 4 | RBAC por perfil; Controle de sessão; MFA/SSO conforme o ambiente; Segregação editorial | 202,5 | Banco + back-end + front-end |
| M02 Canais de comunicação | 810 | 4 | Cadastro de canais e comunidades; Segmentação; Visibilidade; Manutenção | 202,5 | Banco + back-end + front-end |
| M03 Mural, feed e comunicados | 300 | 4 | Publicação; Versionamento; Destaque; Consulta aos comunicados | 75 | Banco + back-end + front-end |
| M04 Aprovação editorial | 810 | 4 | Rascunho; Revisão por pessoa distinta; Aprovação; Publicação auditável | 202,5 | Banco + back-end + front-end |
| M05 Campanhas e calendário | 1.170 | 6 | Briefing; Metas; Peças; Calendário; Monitoramento; Relatórios | 195 | Banco + back-end + front-end |
| M06 Audiências e públicos | 480 | 4 | Grupos; Filtros; Regras de público; Auditoria de segmentação | 120 | Banco + back-end + front-end |
| M07 Contatos e consentimento | 600 | 3 | Cadastro com finalidade; Consentimento e base legal; Preferências | 200 | Banco + back-end + front-end |
| M08 Central de atendimento | 1.140 | 6 | Chamados; Protocolos; Filas; Prioridades; Status; SLA | 190 | Banco + back-end + front-end |
| M09 Chat e mensagens | 400 | 5 | Mensagens; Grupos; Controle de acesso; Histórico; Atualização em tempo real | 80 | Banco + back-end + front-end |
| M10 Envio multicanal | 400 | 7 | Adaptador de e-mail; Adaptador de SMS; Adaptador de push; Opt-out; Filas; Tentativas; Comprovantes | 57,14 | Banco + back-end (integração com o provedor) |
| M11 Portal do cidadão | 600 | 4 | Seções públicas acessíveis; Busca; Formulários; FAQ | 150 | Banco + back-end + front-end |
| M12 Acervo e documentos | 480 | 6 | Upload; Antivírus; Classificação; Miniaturas; Retenção; Controle de acesso | 80 | Banco + back-end + front-end |
| M13 Eventos e agenda | 660 | 5 | Eventos; Inscrições; Agendas; Confirmação; Lembretes | 132 | Banco + back-end + front-end |
| M14 Pesquisa e feedback | 540 | 4 | Questionários; Consentimentos; Respostas; Indicadores | 135 | Banco + back-end + front-end |
| M15 BI e relatórios | 480 | 3 | Painéis por canal, campanha e atendimento; Filtros; Exportações | 160 | Banco + back-end + front-end |
| M16 Integrações e APIs | 600 | 4 | APIs versionadas; Webhooks; Autenticação; Conectores externos | 150 | Back-end + documentação da API |
| M17 LGPD e auditoria | 400 | 4 | Logs protegidos; Retenção; Gestão de pedidos dos titulares; Revisão de acesso | 100 | Banco + back-end + front-end |
| M18 DevOps e transferência | 1.320 | 7 | CI/CD; Ambientes; Observabilidade; Backup; Restauração; Manuais; Release | 188,57 | Configuração, scripts e manual |
