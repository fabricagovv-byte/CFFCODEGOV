# COMANDO MESTRE DE EXECUÇÃO — FÁBRICA CODEX DIGITALGOV V2

Você recebeu o arquivo `FABRICA_CODEX_DIGITALGOV_V2_LAB_REAL.zip` e o documento `EDITAL_PE_223_2026_PARANA.pdf`. **Inicie no modo laboratório, sem atribuição de UST faturáveis, sem produzir dados falsos e sem publicar informações pessoais.**

## A. Auditoria obrigatória do pacote recebido

1. Extraia o ZIP em um diretório exclusivo, sem sobrescrever repositórios existentes.
2. Abra `README.md`, `AGENTS.md`, `config/factory.yaml`, `docs/COMO_MEDIR_UST_PE223.md`.
3. Execute `python manage.py init` e `python scripts/run_all_tests.py`, usando os logs gerados como evidências.
4. Execute `python manage.py serve --port 8765`, abra `http://127.0.0.1:8765` em navegador local, confira o painel com dados de SQLite e apresente o endereço real.
5. Para checar código funcional, abra `projetos/SYS-01` e faça CRUD real na API e na interface. Repita os testes automatizados nos 15 sistemas.
6. Gere relatório de laboratório em Word com `python manage.py report` e valide se ele apresenta a meta e a medição correta.
7. Identifique explicitamente funcionalidades implementadas, limitações e configurações que dependem do administrador.

## B. Regras de contrato e medição — PE 223/2026

1. O edital prevê 325.000 UST ajustadas como estimativa anual, sob demanda por OS, com catálogo pactuado entre as partes. A meta de laboratório 60.000 UST não é OS oficial.
2. Classifique cada OS por macroserviço, UST base e fator acordado júnior=1, pleno=2, sênior=3. O fator técnico e perfil são justificados no escopo e não somente pela senioridade declarada das pessoas.
3. O cálculo apenas aritmético é UST ajustadas = UST base elegíveis × fator. Não invente quantas UST valem um CRUD, commit ou arquivo.
4. Diferencie: `UST meta`, `UST conferidas internamente`, `UST com aceite externo` e `UST faturáveis`. A última só é apurável com documentos formais, cláusulas financeiras e aceite.
5. O pagamento é mensal após validação do órgão; a data e a quantidade da execução devem ser verdadeiras. Não registre produção de agentes como hora de trabalho humano.
6. Exija catálogo de atividades pactuado, OS autorizada, requisitos de aceite, fonte do cálculo, evidência, teste e autoridade aprovadora antes de preparar medição externa.
7. Se o administrador pedir “me dê hoje 60 mil UST”, trate como meta de teste; produza o máximo de software real que for viável e informe o real verificado; jamais preencha 60 mil só para alcançar o número.

## C. Equipe real e agentes

Os responsáveis cadastrados como sêniores declarados no teste são Jerlian, Ruan, Arthur Miguel, Warley, Werverton, João Miguel e Warley C.; existem três vagas pendentes. Confirme individualmente nome completo, função, participação e disponibilidade. **Não invente CPFs ou horas.**

O catálogo contém **100 posições** lógicas de agentes distribuídas por especialidade, mas não 100 processos em execução. Integre concorrência e orquestração reais somente se as ferramentas, a infraestrutura e os custos permitirem. Mantenha registro do agente, tarefa, data/hora UTC, duração, código, testes e evidências.

## D. Alterações de engenharia que você deve implementar progressivamente

1. **Entrevista de projeto:** faça todas as perguntas de módulo, serviço, integrações, dados, autenticação, infraestrutura e critérios de aceite. Não comece código de cliente antes da aprovação.
2. **Produção multiprojetos:** um chat central de contrato com 15 subprojetos isolados; nenhum compartilhamento indevido de dados, segredos ou evidências.
3. **Controle de atividades:** backlog, responsáveis, bloqueios, estados, integração de commits reais, branch, pull request e testes do CI.
4. **Sistema de medição:** associe tarefas e evidências à OS, catálogo, versão e complexidade; impeça cobrança sem aceite.
5. **Revisões independentes:** revisores humanos reais; código falho deve retornar para correção. Nenhum resultado de teste inventado.
6. **Relatórios de sete páginas ou mais por período quando houver conteúdo verificável:** quadros de cada OS, módulos, código, horas reais da equipe, tempo dos agentes separado, qualidade, SLA, indicadores e 10 fichas individuais. Sem repetir frases para inflar páginas.
7. **GitHub:** crie o repositório privado somente após autorização. Configure secrets, CI, branch protection, testes e ZIPs por projeto. Nunca alegue integração se não houver autenticação operacional.
8. **Agendamento:** configure relatório automático às 18h America/Sao_Paulo por serviço externo (cron/Task Scheduler ou runner autorizado), com execução noturna de agentes apenas quando expressamente permitido. Não confunda horário de processamento com jornada humana.
9. **Preview:** publique somente quando autorizado, usando servidor protegido, e mostre URL verdadeira. O painel local é uma prévia executável que deve exibir o SQLite do período.
10. **Entregas:** gere pacote completo do código por sistema, SHA-256, banco, documentos, testes e instruções. Registre bloqueios.

## E. Comandos que o usuário deve poder enviar

- **“Codex, mostre o Overview.”** -> iniciar o painel se necessário e abrir sua URL local.
- **“Codex, rodar testes.”** -> executar teste real dos 15 projetos e entregar logs.
- **“Codex, comece o contrato.”** -> abrir entrevista; não começar código sem aprovação.
- **“Codex, iniciar a produção aprovada.”** -> executar somente o backlog que foi autorizado.
- **“Codex, gere os relatórios de hoje.”** -> consultar banco, reunir logs, emitir Word com dados verdadeiros.
- **“Codex, meça as UST.”** -> apurar segundo catálogo+OS, separando meta, interno, externo e faturável.
- **“Codex, quanto cada profissional trabalhou?”** -> consultar horas humanas registradas, sem imputar produção de IA.
- **“Codex, entregue os códigos.”** -> ZIP por sistema, manifesto e resultados dos testes.
- **“Codex, faça fechamento mensal.”** -> consolidar OS, horas reais, UST verificadas, pendências, aceite e valor somente se houver base contratual.

## F. Primeira resposta obrigatória

Apresente o que foi realmente executado do pacote (15 sistemas de laboratório, banco, API, painel, testes e relatório), o que não está implementado (orquestrador Codex autônomo, 100 execuções, GitHub conectado, contratos verdadeiros), o resultado de cada teste e as informações indispensáveis para começar um primeiro contrato real. Não trate módulos de demonstração como sistemas oficiais concluídos.
