# Plano de Gestão da Execução Contratual (GEC) — PE-223-2026-PR

Gerado em 2026-11-06T00:44:50-03:00 pelo Planejador GEC (G04) com apoio de G02, G21, G22, G23 e G24. Itens **a preencher** dependem do edital ou do responsável.

> **Legenda:** ESTIMATIVA = planejado/calculado antes da execução · REAL = comprovado (auditado) ou aceito pelo órgão. Cada exigência indica a origem (documento, cláusula, página).

## 1. Identificação do contrato

| Campo | Valor |
|---|---|
| Órgão contratante | Estado do Paraná — SEAP/DECON/Departamento de Logística (p. 1) |
| Esfera | estadual |
| Contrato / processo / edital | a definir (após homologação) / Protocolo nº 24.481.744-0 / Pregão Eletrônico nº 223/2026 (nº interno GMS); nº Compras.gov 36/2026; UASG 928658 |
| Regime jurídico | Lei Federal nº 14.133/2021, Decreto Estadual nº 10.086/2022 e LC nº 123/2006. Serviço de natureza contínua, modelo de exaustão do saldo contratado, medido em UST. Minuta padronizada PGE/PR para 'prestação de serviços sem dedicação exclusiva de mão de obra'. Recursos com apoio do BIRD (Projeto Paraná Eficiente, componente PforR). Consórcio e subcontratação vedados. Regime de execução (empreitada etc.): não consta. |
| Vigência | **a preencher** a **a preencher** |
| Valor global | não consta nas páginas lidas. O TR 9.1 informa que o valor estimado foi 'detalhado em documento separado e classificado'. |
| Gestor / fiscal do contrato | **a preencher** / **a preencher** |
| Preposto da contratada | **a preencher** |

## 2. Objeto e escopo

**Objeto:** Contratação de empresa especializada em serviços de desenvolvimento de software personalizado (Custom Software Development – CSD), conforme estudos da Gartner, abrangendo sustentação, desenvolvimento, manutenção e evolução de sistemas, em modelo de catálogo de serviços estruturado em Unidades de Serviço Técnico (UST). O TR descreve ainda suporte (1º, 2º e 3º níveis), infraestrutura, DevOps, BI/Ciência de Dados, IA, gestão de projetos, jornada do cidadão, governança, segurança da informação e integração (15 itens).

Tecnologias obrigatórias: a preencher · Banco: **a preencher** · Infraestrutura: **a preencher**

Matriz de rastreabilidade completa: `MATRIZ_RASTREABILIDADE.md`.

## 3. Serviços contratados — explicação técnica

| Código | Serviço | Explicação técnica | Unidade | Origem |
|---|---|---|---|---|
| 01 | Serviços de suporte técnico de 1º Nível | Atendimento remoto de questões básicas de hardware, software e rede para usuários de TI. Corresponde a um service desk de primeiro contato, com tarefas triviais existentes em base de conhecimento (fator 1 na tabela). | UST | p022 (TR 1.4.1.1); p020 (tabela 1.3) |
| 02 | Serviços de suporte técnico de 2º Nível | Atendimento presencial de questões básicas de hardware, software e rede. O texto diferencia o 2º nível do 1º apenas pela forma presencial de atendimento, não pela complexidade técnica. | UST | p022 (TR 1.4.2.1); p020 |
| 03 | Serviços de suporte técnico de 3º Nível | Sustentação de infraestrutura de redes e segurança (LAN/WAN, roteadores/switches, IPS/firewall, testes de invasão, patches, GPOs, antivírus), administração de servidores (Linux/Microsoft, AD, DNS, DHCP, IIS, Exchange, clusters, virtualização, backup/restore) e administração de bancos de dados (tuning, segurança, backup/recovery, privilégios). Inclui atividades rotineiras, periódicas e um setor de atendimento técnico responsável pelos postos e por suporte telefônico. | UST | p022–p029 (TR 1.4.3, 1.4.3.1, 1.4.3.1.1, 1.4.3.1.2, 1.4.3.2, 1.4.3.2.1, 1.4.3.2.2, 1.4.3.3); p020 |
| 04 | Serviços de Sustentação de Sistemas | Manutenção corretiva, preventiva, adaptativa (mudanças legais/normativas) e de segurança de sistemas em produção e seus bancos de dados, com atualização de bibliotecas, monitoramento de disponibilidade/performance e gestão de incidentes e problemas com análise de causa raiz. Inclui controle de mudanças/versionamento com rastreabilidade, suporte a integrações legadas, otimização de consultas e criação de silos de dados. | UST | p029–p030 (TR 1.4.4.1 a 1.4.4.3); p020 |
| 05 | Serviços de Desenvolvimento de Sistemas | Construção de sistemas, portais, sistemas web e apps móveis, com modelagem de dados e integração com sistemas externos/legados, em Java, PHP, React, Next.js, Python ou outras linguagens de código aberto, compatível com PostgreSQL, MySQL, SQL Server e Oracle. Abrange também arquitetura de sistemas (visões funcional, de linguagem, estrutural e física) e análise/qualidade de software (requisitos, processos AS-IS/TO-BE, testes), com método ágil e padrões CMMI ou MPS.BR. | UST | p030–p032 (TR 1.4.5.1, 1.4.5.2, 1.4.5.3); p020 |
| 06 | Serviços de Testes de Sistemas | Planejamento e execução de testes manuais e automatizados (funcionais, regressão, integração, usabilidade), UAT com usuários-chave e testes em homologação/pré-produção. Inclui gestão de defeitos, evidências (prints, logs, relatórios), indicadores (TDC, VAE, taxa de aprovação, cobertura) e manutenção de artefatos de QA como plano de testes e matriz de rastreabilidade. | UST | p032–p033 (TR 1.4.6.1, 1.4.6.2); p020 |
| 07 | Serviços de Análise de Negócios e Processos | Análise de negócio da área específica de cada projeto de TI no contexto da administração pública. Inclui mapeamento, modelagem e redesenho de processos com BPMN. | UST | p033 (TR 1.4.7.1); p020 |
| 08 | Serviços de Implementação DevOps | Implementação de ferramentas, processos e infraestrutura de DevOps com arquitetura de containers e orquestração de aplicações. O objeto relaciona o serviço à integração contínua e à entrega ágil de soluções. | UST | p033 (TR 1.4.8.1); p019 (TR 1.1 alínea d); p020 |
| 09 | Serviços de Business Intelligence (BI) e Ciência de Dados | Soluções de BI e Data Warehouse (requisitos de dados, modelagem multidimensional, indicadores, mapas ETL, camada visual, implantação) e de data lake/big data (arquitetura, modelagem, administração). Inclui algoritmos de análise de dados, reconhecimento de padrões, fala/escrita, visão computacional, estatística avançada e redes neurais, além de processos de inovação incremental. | UST | p033–p034 (TR 1.4.9.1); p020 |
| 10 | Serviços de Desenvolvimento de IA | Desenvolvimento de algoritmos e tecnologias de Inteligência Artificial com as tecnologias mais atuais de mercado, conforme a necessidade do contratante. O TR não detalha atividades, artefatos nem critérios específicos para este item. | UST | p034 (TR 1.4.10.1); p020 |
| 11 | Serviços de Gerenciamento de Projetos | Apoio à definição, melhoria e institucionalização de metodologias de gestão de projetos. Inclui acompanhamento de portfólio, programas e projetos e extração de relatórios gerenciais. | UST | p034 (TR 1.4.11.1, 1.4.11.2); p020 |
| 12 | Serviços para Jornada do Cidadão | Análise e melhoria da experiência do cidadão em serviços digitais: Linguagem Simples (tradução, organização da informação, automação), portais e automação de transparência, mapeamento da jornada com indicadores de satisfação. Inclui acessibilidade digital conforme WCAG e eMAG e recursos assistivos (leitores de tela, comandos de voz). | UST | p034–p035 (TR 1.4.12.1, 1.4.12.1.1); p020 |
| 13 | Serviços de Governança de TI | Estruturação de modelos de governança (análise de maturidade; apoio à implantação de COBIT, ITIL, CMMI, MPS.BR, PMI, TOGAF), gestão da informação (fluxos, governança de dados e documentos, políticas de acesso/classificação/preservação) e auditoria/conformidade. Inclui gestão de riscos e continuidade (planos de contingência e resposta a incidentes) e gestão de portfólio com metodologia ágil. | UST | p035–p036 (TR 1.4.13.1, 1.4.13.1.1); p020 |
| 14 | Serviços de Gestão de Segurança da Informação | Construção de políticas de segurança (análise de riscos, normativos, controles alinhados a ISO 27001, NIST e ITIL), implantação da LGPD (diagnóstico, plano de ação, mapeamento e classificação de dados pessoais, programa contínuo de auditoria). Inclui implantação de controles de segurança e gestão de identidade e acesso, resposta a incidentes, PCN e monitoramento contínuo de ameaças. | UST | p036–p037 (TR 1.4.14.1); p020 |
| 15 | Serviços de Integração de Sistemas | Planejamento/arquitetura de integrações (multi-inquilino, escalável, segura), desenvolvimento e publicação de APIs institucionais com versionamento e rollback, integração com legados, nuvem, bancos SQL/NoSQL e ferramentas de BI, fluxos orquestrados com consistência transacional, observabilidade e logs de auditoria. Este item também exige que a CONTRATADA forneça, sem custos adicionais, quatro soluções tecnológicas: gestão de serviços de TIC (ITSM), monitoramento, gestão de projetos de TIC e gestão de integrações (low-code). | UST | p037–p044 (TR 1.4.15, 1.4.15.1, 1.4.15.2, 1.4.15.3, 1.4.15.4); p020 |

## 4. Equipe exigida × equipe designada

| Perfil exigido | Qtd | Requisitos | Origem |
|---|---|---|---|
| Preposto (e substitutos) | 1 | — | p049 (TR 6.1.1 Reunião Inicial); p051 (workshop); p052–p053; p068 (TR 16.2) |
| Responsável pelo acompanhamento da execução (regularidade técnica e disciplinar da equipe e contato com o CONTRATANTE) | 1 | — | p062 (TR 11.2.1.2) |
| Responsáveis técnicos (e substitutos) | 1 | — | p051 (TR 6.1.1 – capacitação); p052 (reuniões de acompanhamento) |
| Equipe técnica que executa as OS – exemplos citados: arquitetos, analistas de requisitos, analistas de negócios, desenvolvedores | 1 | — | p051 (TR 6.1.1 – Envolvidos) |
| Níveis de senioridade Júnior / Pleno / Sênior (vinculados ao fator de complexidade 1/2/3) | 1 | — | p021 (TR 1.3.1) |
| Perfis profissionais requeridos por OS | 1 | — | p020–p021 (TR 1.3) |
| Equipe indicada na habilitação (qualificação técnica) – deve executar os serviços | 1 | — | p064 (TR 11.2.1.19 e 11.2.1.20) |

**Designados:**

- Jerlian — Arquitetura e desenvolvimento sênior
- Ruan — Backend e sustentação sênior
- Arthur Miguel — Gestão e governança sênior
- Warley — Frontend e integrações sênior
- Werverton — DevOps e integrações sênior
- João Miguel — Dados e IA sênior
- Warley C. — QA, análise e segurança sênior

Confronto completo edital × documento base: `CONFRONTO_EDITAL.md`.

## 5. Organização: agentes de IA e responsabilidade humana

| Etapa | Agentes de IA | Responsável humano (aprova) |
|---|---|---|
| Leitura do edital, habilitação, SLAs | G02, G21, G23 | Gestor do contrato |
| Planejamento, cronograma, custos | G04, G24, G22 | Gerente de projeto |
| Arquitetura e desenvolvimento | G05, G06–G09, E01–E13 | Responsável técnico |
| Testes, revisão, segurança | G12, G13, G10, E16–E18 | Responsável técnico |
| Evidências, medição, relatórios | G17, G15, G16, G19 | Gerente de projeto / preposto |
| Homologação e entrega | G20, G11 | Fiscal do órgão (aceite) |

Total: 44 agentes de IA (lista em `fabrica/docs/EQUIPE_AGENTES.md`).

## 6. Planejamento por projeto (ESTIMATIVA)

Sem PLANEJAMENTO.csv preenchido: o plano por projeto, o cronograma diário/mensal e as mensalidades aparecem aqui quando o responsável preencher o plano.

## 9. Medição e cálculos

- Modalidade: UST · Metodologia: UST base × fator de complexidade 1/2/3 por OS; catálogo detalhado a pactuar (TR 1.3, 1.3.1, 1.3.2, p. 19-22) · Fórmula: **a preencher**
- Quantidade contratada: 325.000 UST ajustadas (130.000 base) — referencial, consumo só por OS (p. 136) · Valor unitário: **a preencher**
- Medição parcial: consumo sob demanda por OS; sem volume mínimo (p. 59, 156)


- Pontos de função: contagem pela metodologia do contrato (G16); produtividade h/PF não informada.
- Regras: previsto = OS; comprovado = auditoria aprovada; aceito = documento do órgão. UST/PF/horas só se convertem pela fórmula do contrato.

## 10. Custos estimados por perfil (ESTIMATIVA)

Depende do planejamento.

## 11. Documentos de habilitação

| Grupo | Documento | Exigência | Origem | Situação |
|---|---|---|---|---|
| outros | Certificado de Regularidade de Registro Cadastral (SICAF ou CAUFPR) | Emitido pelo SICAF ou pelo Cadastro Unificado de Fornecedores do Estado do Paraná (CAUFPR), acompanhado dos documentos dos itens 1.4, 1.5, 1.6 e 1.7 do Anexo II. Quem não tiver documentos válidos no SICAF/CAUFPR deve apresentar todos os documentos listados no Anexo II. | p173 — Edital Anexo II item 1.1 | a verificar |
| jurídica | Prova de Registro Comercial (empresa individual) | Aplicável no caso de empresa individual. | p123 — TR Anexo I.III item 1.1; p173 — Edital Anexo II item 1.2/1.1 | a verificar |
| jurídica | Ato constitutivo, Estatuto ou Contrato Social e Aditivo em vigor | Devidamente registrados (sociedades comerciais); para sociedades por ações, acompanhado de documentos de eleição dos administradores. | p123 — TR Anexo I.III item 1.2; p173 — Edital Anexo II item 1.2 | a verificar |
| jurídica | Inscrição do Ato Constitutivo (sociedades civis) com prova da diretoria em exercício | Aplicável a sociedades civis. | p123 — TR Anexo I.III item 1.2.1; p173 — Edital Anexo II item 1.2.1 | a verificar |
| jurídica | Decreto de autorização (empresa/sociedade estrangeira) e ato de registro/autorização de funcionamento | Para empresa estrangeira em funcionamento no País; ato de registro quando a atividade exigir. | p123 — TR Anexo I.III item 1.2.2; p173 — Edital Anexo II item 1.2.2 | a verificar |
| fiscal-trabalhista | Prova de inscrição no CNPJ | Cadastro Nacional da Pessoa Jurídica. | p123 — TR Anexo I.III item 2.1.1; p173 — Edital Anexo II item 1.3.1 | a verificar |
| fiscal-trabalhista | Certidão Conjunta Negativa de Débitos relativos a Tributos Federais e à Dívida Ativa da União (RFB/PGFN) | Dentro do prazo de validade; conforme Decreto Federal nº 5.512/2005. | p123 — TR Anexo I.III item 2.1.2 a; p173 — Edital Anexo II item 1.3.2 a | a verificar |
| fiscal-trabalhista | Regularidade com a Fazenda Pública Estadual | Certidão Negativa de Existência de Débitos inscritos na Dívida Ativa Estadual e certidões negativas de débitos estaduais. | p123 — TR Anexo I.III item 2.1.2 b; p173 — Edital Anexo II item 1.3.2 b | a verificar |
| fiscal-trabalhista | Regularidade com a Fazenda Pública Municipal | Certidão Negativa de Existência de Débitos inscritos na Dívida Ativa Municipal e certidões negativas de débitos municipais. Texto diz "da sede da CONTRATANTE" (ver conflitos). | p123 — TR Anexo I.III item 2.1.2 c; p173 — Edital Anexo II item 1.3.2 c | a verificar |
| fiscal-trabalhista | Regra de filial (documentos jurídicos e fiscais em nome da filial) | Se a licitante for filial, documentos de habilitação jurídica e regularidade fiscal em nome da filial, exceto os emitidos somente em nome da matriz. ME/EPP com restrição fiscal: 5 dias úteis (prorrogáveis por igual período) a partir da declaração de vencedor; não regularização = decadência do direito à contratação. | p123–p124 — TR Anexo I.III itens 2.1.3–2.1.5; p173–p174 — Edital Anexo II itens 1.3.3–1.3.5 | a verificar |
| fiscal-trabalhista | Declaração de não emprego de menor (art. 7º, XXXIII, CF) | Nenhum menor de 18 anos em trabalho noturno, perigoso ou insalubre; nenhum menor de 16 anos, salvo aprendiz a partir de 14 anos. Texto remete ao "Anexo II" (modelo efetivo está no Anexo V item 2, p185). | p124 — TR Anexo I.III item 2.2.1; p174 — Edital Anexo II item 1.4.1; p185 — Anexo V item 2 | a verificar |
| fiscal-trabalhista | Certidão Negativa de Débitos Trabalhistas (Justiça do Trabalho) | Admite-se Certidão Positiva com Efeitos de Negativa nos termos da CLT. | p124 — TR Anexo I.III item 2.2.2; p174 — Edital Anexo II item 1.4.2 | a verificar |
| econômico-financeira | Certidão negativa de falência, recuperação judicial ou execução patrimonial | Expedida pelo distribuidor da sede da pessoa jurídica; validade = a constante na própria certidão. | p124 — TR Anexo I.III item 2.3.1; p174 — Edital Anexo II item 1.5.1 | a verificar |
| econômico-financeira | Balanço patrimonial, DRE e demais demonstrações contábeis dos 2 últimos exercícios sociais | Vedada substituição por balancetes ou balanços provisórios; podem ser atualizados por índices oficiais. | p124 — TR Anexo I.III item 2.3.2; p174 — Edital Anexo II item 1.5.2 | a verificar |
| econômico-financeira | Índices LG, SG e LC já calculados | LG = (AC + RLP) / (PC + PNC) >= 1,0; SG = Ativo Total / (PC + PNC) >= 1,0; LC = AC / PC >= 1,0. Vale para empresas cadastradas ou não no PNCP. O Edital (não o TR) exige apresentar os índices JÁ CALCULADOS, com assinatura do contador e do representante legal. | p125 — TR Anexo I.III itens 2.3.3–2.3.4; p174 — Edital Anexo II itens 1.5.3–1.5.5 | a verificar |
| econômico-financeira | Comprovação de patrimônio líquido mínimo | PL não inferior a 10% do valor total estimado anual da contratação, pelo balanço e demonstrações do último exercício, já exigíveis; vedados balancetes/balanços provisórios. Valor estimado anual: não consta nas páginas lidas. | p125 — TR Anexo I.III item 2.3.5; p175 — Edital Anexo II item 1.5.6 | a verificar |
| técnica | Atestado (a) — desenvolvimento, sustentação e manutenção corretiva e adaptativa | >= 20.000 UST (50% da quantidade anual ajustada do item 04 — Sustentação de Sistemas) | p126 — TR item 2.4.6 a; p175 — Edital Anexo II item 1.6.6 a | a verificar |
| técnica | Atestado (b) — desenvolvimento e sustentação sob metodologias ágeis (Scrum ou equivalente) | Sem quantitativo; um ou mais contratos | p126–p127 — TR item 2.4.6 b; p175 — Edital 1.6.6 b | a verificar |
| técnica | Atestado (c) — sustentação sob práticas DevOps com contêineres e orquestração | Sem quantitativo; um ou mais contratos | p127 — TR 2.4.6 c; p176 — Edital 1.6.6 c | a verificar |
| técnica | Atestado (d) — back-end Python + SGBD relacional (PostgreSQL, MySQL, SQL Server ou Oracle) | >= 10.000 UST; 'experiência sobre versões da tecnologia lançadas' (frase incompleta) | p127 — TR 2.4.6 d; p176 — Edital 1.6.6 d | a verificar |
| técnica | Atestado (e) — back-end PHP + SGBD relacional | >= 10.000 UST | p127 — TR 2.4.6 e; p176 — Edital 1.6.6 e | a verificar |
| técnica | Atestado (f) — manutenção de sistemas em Python ou PHP | >= 20 aplicações distintas; somatório admitido | p127 — TR 2.4.6 f; p176 — Edital 1.6.6 f | a verificar |
| técnica | Atestado (g) — front-end React.js, Next.js ou Vue.js | >= 10.000 UST; atualidade tecnológica da alínea d | p127 — TR 2.4.6 g; p176 — Edital 1.6.6 g | a verificar |
| técnica | Atestado ou declaração (h) — uso de ferramenta de gestão de projetos aderente a CMMI, MPS.BR ou equivalente | Sem quantitativo | p127 — TR 2.4.6 h; p176 — Edital 1.6.6 h | a verificar |
| técnica | Atestado (i) — desenvolvimento e sustentação mobile (Android e iOS) | >= 5.000 UST | p127 — TR 2.4.6 i; p176 — Edital 1.6.6 i | a verificar |
| técnica | Atestado (j) — soluções web de BI, Data Warehouse e ETL, incluindo capacitação de usuários | >= 5.000 UST | p127–p128 — TR 2.4.6 j; p176 — Edital 1.6.6 j | a verificar |
| técnica | Atestado (k) — migração de dados entre sistemas ou bases | Sem quantitativo | p128 — TR 2.4.6 k; p176 — Edital 1.6.6 k | a verificar |
| técnica | Atestado (l) — atendimento de 2º nível com administração de legados e infraestrutura (BD, backup, armazenamento, virtualização, aplicações web, mensageria) | >= 5.000 UST | p128 — TR 2.4.6 l; p176 — Edital 1.6.6 l | a verificar |
| técnica | Comprovação (m) — maturidade CMMI-DEV nível 3+ ou MPS.BR-SW nível C+ | Certificado vigente OU equivalência com evidência datada das 7 práticas (requisitos/rastreabilidade, planejamento, monitoramento, QA, configuração, medição, processo organizacional institucional) | p128 — TR 2.4.6 m; p176–p177 — Edital 1.6.6 m | a verificar |
| técnica | Comprovação (n) — gestão de serviços ISO/IEC 20000, CMMI-SVC nível 2+ ou MPS.BR-Serviços nível F+ | Certificado vigente OU evidência datada de 6 processos (catálogo, SLA medido, incidentes, requisições/mudanças, configuração, relato periódico) | p128–p129 — TR 2.4.6 n; p177 — Edital 1.6.6 n | a verificar |
| técnica | Comprovação (o) — SGSI compatível com ISO/IEC 27001 | Certificado vigente OU evidência datada de 6 itens (política aprovada, gestão de riscos, declaração de aplicabilidade, incidentes, controle de acesso/ativos, análise crítica e auditoria interna) | p129 — TR 2.4.6 o; p177 — Edital 1.6.6 o | a verificar |
| técnica | Comprovação (p) — privacidade ISO/IEC 27701 / LGPD | Certificado vigente OU evidência datada de 6 itens (política, ROPA, nomeação do DPO, RIPD/DPIA quando aplicável, atendimento a titulares, incidentes com dados pessoais) | p129–p130 — TR 2.4.6 p; p177 — Edital 1.6.6 p | a verificar |
| técnica | Atestado (q) — suporte e administração de infraestrutura de redes N3 | >= 5.000 UST; somatório admitido | p130 — TR 2.4.6 q; p177 — Edital 1.6.6 q | a verificar |
| técnica | Atestado (r) — suporte técnico N1 e/ou N2 | >= 10.000 UST, dos quais >= 5.000 UST em UM ÚNICO contrato (única exceção ao somatório) | p130 — TR 2.4.6 r; p177 — Edital 1.6.6 r | a verificar |
| técnica | Atestado (s) — gestão e monitoramento de ambientes de infraestrutura de TI | Sem quantitativo; admite evidências do ambiente, com sigilo do cliente | p130 — TR 2.4.6 s; p178 — Edital 1.6.6 s | a verificar |
| técnica | Atestado (t) — mapeamento e modelagem de processos e análise de negócios | >= 10.000 UST | p130 — TR 2.4.6 t; p178 — Edital 1.6.6 t | a verificar |
| técnica | Atestado (u) — projetos aderentes à Lei 13.460/2017 e à LGPD | Sem quantitativo | p130 — TR 2.4.6 u; p178 — Edital 1.6.6 u | a verificar |
| técnica | Atestado (v) — integração com login único governamental (gov.br ou equivalente) | Sem quantitativo | p130 — TR 2.4.6 v; p178 — Edital 1.6.6 v | a verificar |
| técnica | Atestado (w) — integração com assinatura eletrônica governamental (gov.br ou equivalente) | Sem quantitativo | p130 — TR 2.4.6 w; p178 — Edital 1.6.6 w | a verificar |
| técnica | Atestado (x) — solução aderente à Lei 14.063/2020 (assinatura eletrônica) | Sem quantitativo | p130 — TR 2.4.6 x; p178 — Edital 1.6.6 x | a verificar |
| técnica | Atestado (y) — projetos com inteligência artificial | Mínimo: integração com modelos de IA por API, tratamento e auditabilidade dos dados, conformidade com proteção de dados | p130–p131 — TR 2.4.6 y; p178 — Edital 1.6.6 y | a verificar |
| técnica | Atestado (z) — conteúdo de capacitação EaD em LMS de código aberto (Moodle, Open edX, Chamilo, Canvas comunitário ou equivalente) | Sem quantitativo mínimo de UST; sem plataforma proprietária | p131 — TR 2.4.6 z; p178 — Edital 1.6.6 z | a verificar |
| técnica | Datação externa de cada documento apresentado (regra geral) | Cada documento deve ter data comprovada por meio externo verificável (assinatura eletrônica avançada/qualificada — gov.br ou ICP-Brasil —, carimbo de tempo, protocolo/registro em sistema de terceiro ou publicação oficial). Não se aceita data autodeclarada/interna. | p131 — TR Anexo I.III, regra geral de equivalência; p178 — Edital Anexo II, regra geral | a verificar |
| declarações | Declaração única do Anexo V | Conhecimento do edital e posse das condições de habilitação; (1) inexistência de fato impeditivo (art. 14 da Lei 14.133/2021 — vínculos com dirigentes/agentes até 3º grau; sem condenação em 5 anos por trabalho infantil/escravo); (2) não utilização de mão de obra de menores; (3) atendimento à política ambiental de licitação sustentável (logística reversa); (4) reserva de cargos para PcD e reabilitados (art. 63, IV). | p185 — Anexo V | a verificar |
| declarações | Declaração de ausência de nepotismo (Decreto Estadual nº 2.485/2019) | Modelo do Anexo VI. | p186 — Anexo VI | a verificar |
| declarações | Termo de Vistoria | Modelo do Anexo VII-02, com assinatura do representante e do servidor responsável. Se a vistoria é obrigatória ou facultativa: não consta nas páginas lidas. | p187 — Anexo VII (02 – Termo de Vistoria) | a verificar |
| declarações | Declaração de Conhecimento (das condições locais) | Modelo do Anexo VII-03. Relação com o Termo de Vistoria (alternativa ou cumulativa) — não consta nas páginas lidas. | p188 — Anexo VII (03 – Declaração de Conhecimento) | a verificar |
| declarações | Procuração (se houver representante) | Modelo do Anexo IV, acompanhada de cópia do documento oficial de identidade do outorgado. | p184 — Anexo IV | a verificar |
| outros | Item 1.7 do Anexo II (referido no item 1.1) | Não consta nas páginas lidas (o item 1.1 manda apresentar os itens 1.4–1.7; o item 1.7 não aparece em p173–p178). | p173 — Edital Anexo II item 1.1 | a verificar |
| outros | Prova de Conceito (PoC) — etapa eliminatória após a habilitação | Só para a 1ª colocada já habilitada; demandas de no mínimo 500 UST em 5 dias úteis (08–12h e 14–18h); equipe nomeada com remuneração comprovada; nomes enviados com 2 dias úteis de antecedência; Termo de Confidencialidade; tecnologias de código aberto; vedada IA generativa; custos da licitante; produto executável e sem erros. | p090–p099 — TR item 24 (24.1.3, 24.2.8, 24.3.3, 24.3.4, 24.3.11, 24.3.21, 24.3.22, 24.3.24, 24.3.25) | a verificar |

## 12. Níveis de serviço (SLA) e glosas

| Indicador | Meta | Como medir | Glosa | Origem |
|---|---|---|---|---|
| Suspender ou interromper, salvo motivo de força maior ou caso fortuito, os serviços contratuais | Zero ocorrências (não consta meta numérica) | Contagem por dia e por unidade de atendimento ('unidade de atendimento' não definida nas páginas lidas) | Grau 4 = 1,6% ao dia sobre o valor mensal do contrato, por dia e por unidade de atendimento | p070, TR item 18.6, tabela ANS item 1 |
| Manter funcionário sem qualificação para executar os serviços contratados | Zero ocorrências (critério de 'qualificação' não consta nas páginas lidas) | Por empregado e por dia | Grau 3 = 0,8% ao dia sobre o valor mensal do contrato, por empregado e por dia | p070, TR item 18.6, tabela ANS item 2 |
| Recusar-se a executar serviço determinado pela fiscalização | Zero ocorrências | Por serviço e por dia | Grau 2 = 0,4% ao dia sobre o valor mensal do contrato, por serviço e por dia | p070, TR item 18.6, tabela ANS item 3 |
| Indisponibilidade de Plataforma por um período superior a 24 (vinte e quatro) horas | Indisponibilidade contínua não superior a 24 horas ('Plataforma' não definida nas páginas lidas; não consta meta de disponibilidade percentual) | Duração da indisponibilidade em horas; forma de aferição (ferramenta, janela, exclusões) não consta | Grau 3 = 0,8% ao dia sobre o valor mensal do contrato | p070, TR item 18.6, tabela ANS item 4 |
| Deixar de atender chamado aberto para correção de falha na plataforma | Atender todo chamado de correção de falha (prazo de atendimento/solução não consta nas páginas lidas) | Por chamado não atendido; unidade de contagem não consta | Grau 4 = 1,6% ao dia sobre o valor mensal do contrato | p070, TR item 18.6, tabela ANS item 5 |
| Deixar de cumprir determinação formal ou instrução complementar do órgão fiscalizador | Zero ocorrências | Por ocorrência | Grau 2 = 0,4% ao dia sobre o valor mensal do contrato, por ocorrência | p070, TR item 18.6, tabela ANS item 6 (bloco 'Para os itens a seguir, deixar de:') |
| Deixar de substituir empregado que se conduza de modo inconveniente ou não atenda às necessidades do serviço | Zero ocorrências | Por funcionário e por dia | Grau 1 = 0,2% ao dia sobre o valor mensal do contrato, por funcionário e por dia | p070, TR item 18.6, tabela ANS item 7 |
| Deixar de cumprir quaisquer dos itens do Edital e seus Anexos não previstos nesta tabela, após reincidência formalmente notificada pelo órgão fiscalizador | Zero reincidências notificadas | Por item e por ocorrência; por funcionário e por dia (o texto traz as duas unidades) | Grau 3 = 0,8% ao dia sobre o valor mensal do contrato | p070-p071, TR item 18.6, tabela ANS item 8 |
| Deixar de indicar e manter durante a execução do contrato os prepostos previstos no edital/contrato | Preposto indicado e mantido continuamente (CONTRATO 10.1.1, p144) | Por funcionário e por dia | Grau 1 = 0,2% ao dia sobre o valor mensal do contrato, por funcionário e por dia | p071, TR item 18.6, tabela ANS item 9 |
| Deixar de providenciar treinamento para seus funcionários conforme previsto na relação de obrigações da CONTRATADA | Treinamentos previstos realizados (conteúdo/carga não constam nas páginas lidas) | Por funcionário e por dia | Grau 1 = 0,2% ao dia sobre o valor mensal do contrato, por funcionário e por dia | p071, TR item 18.6, tabela ANS item 10 |
| Deixar de registrar e controlar, diariamente, a assiduidade e a pontualidade de seu pessoal | Registro diário de assiduidade e pontualidade de todo o pessoal | Por empregado e por dia | Grau 4 = 1,6% ao dia sobre o valor mensal do contrato, por empregado e por dia | p071, TR item 18.6, tabela ANS item 11 |
| Deixar de manter, durante a execução do contrato, todas as condições de habilitação e qualificação exigidas na licitação | Habilitação e qualificação mantidas durante toda a vigência | Por empregado e por dia | Grau 4 = 1,6% ao dia sobre o valor mensal do contrato, por empregado e por dia | p071, TR item 18.6, tabela ANS item 12 |
| Não apresentar, quando solicitado, documentação fiscal, trabalhista e previdenciária, sem motivo justificável (redação com dupla negação por estar sob 'deixar de') | Apresentar a documentação sempre que solicitado (prazo de apresentação não consta) | Por empregado e por dia | Grau 5 = 3,2% ao dia sobre o valor mensal do contrato, por empregado e por dia | p071, TR item 18.6, tabela ANS item 13 |
| Deixar de garantir a manutenção de empregado em serviço durante o expediente | Empregado em serviço durante todo o expediente (horário do expediente não consta nas páginas lidas) | Por empregado e por dia | Grau 5 = 3,2% ao dia sobre o valor mensal do contrato, por empregado e por dia | p071, TR item 18.6, tabela ANS item 14 |
| Deixar de substituir empregado que tenha conduta inconveniente ou incompatível com suas atribuições | Zero ocorrências | Por empregado e por dia | Grau 4 = 1,6% ao dia sobre o valor mensal do contrato, por empregado e por dia | p071, TR item 18.6, tabela ANS item 15 |
| Deixar de cumprir horários estabelecidos pelo contrato ou determinados pela Fiscalização | Cumprimento integral dos horários (horários não constam nas páginas lidas) | Por empregado e por dia | Grau 4 = 1,6% ao dia sobre o valor mensal do contrato, por empregado e por dia | p071, TR item 18.6, tabela ANS item 16 |
| (Deixar de) Entregar ou entregar com atraso documentação exigida no contrato | Documentação exigida entregue no prazo (prazos específicos não constam nas páginas lidas) | Unidade de contagem não consta | Grau 3 = 0,8% ao dia sobre o valor mensal do contrato | p071, TR item 18.6, tabela ANS item 17 |
| Deixar de efetuar o recolhimento mensal do FGTS e/ou das contribuições sociais previdenciárias dos empregados | Recolhimento mensal em dia | Por empregado e por dia | Grau 5 = 3,2% ao dia sobre o valor mensal do contrato, por empregado e por dia | p071, TR item 18.6, tabela ANS item 18 |
| Deixar de garantir empregado com qualificação para a execução dos serviços | Todos os empregados qualificados (critério não consta nas páginas lidas) | Por empregado e por dia | Grau 5 = 3,2% ao dia sobre o valor mensal do contrato, por empregado e por dia | p071, TR item 18.6, tabela ANS item 19 |
| Deixar de executar serviço completo, com qualidade | Serviço completo e com qualidade (critério de qualidade não consta nas páginas lidas) | Unidade de contagem não consta | Grau 4 = 1,6% ao dia sobre o valor mensal do contrato | p071, TR item 18.6, tabela ANS item 20 |
| Deixar de garantir o pagamento mensal de salários, férias, vale-transporte | Pagamentos trabalhistas em dia | Por empregado e por dia | Grau 4 = 1,6% ao dia sobre o valor mensal do contrato, por empregado e por dia | p071, TR item 18.6, tabela ANS item 21 |
| Deixar de zelar pelas instalações da CONTRATANTE | Zero ocorrências | Unidade de contagem não consta | Grau 3 = 0,8% ao dia sobre o valor mensal do contrato | p071, TR item 18.6, tabela ANS item 22 |
| Deixar de iniciar, não suspender ou não interromper os serviços contratados, salvo motivo de força maior | Início no prazo e continuidade dos serviços | Unidade de contagem não consta | Grau 5 = 3,2% ao dia sobre o valor mensal do contrato | p071, TR item 18.6, tabela ANS item 23 |
| Deixar de efetuar a IMEDIATA reposição de empregados faltosos | Reposição imediata (prazo em horas não consta) | Por empregado e por dia | Grau 5 = 3,2% ao dia sobre o valor mensal do contrato, por empregado e por dia | p071, TR item 18.6, tabela ANS item 24 |
| Deixar de garantir que seus funcionários não destruam nem danifiquem patrimônio da contratante | Zero ocorrências | Por empregado e por dia | Grau 4 = 1,6% ao dia sobre o valor mensal do contrato, por empregado e por dia | p072, TR item 18.6, tabela ANS item 25 |
| Manter nas dependências da CONTRATANTE quaisquer equipamentos ou materiais, previstos em contrato, sem autorização prévia do CONTRATANTE (redação ambígua sob 'deixar de') | Zero ocorrências | Unidade de contagem não consta | Grau 3 = 0,8% ao dia sobre o valor mensal do contrato | p072, TR item 18.6, tabela ANS item 26 |

## 13. Relatórios e evidências

- Relatórios exigidos: Relatório mensal sobre a prestação dos serviços, Relatórios de execução (elaborados pela contratada e validados pelo fiscal), Relatórios gerenciais / relatórios periódicos, Relatório/documentação final de transferência de conhecimento, Relatórios técnicos de conformidade com políticas e normas de segurança, Relatório da taxa de transmissão dos links ativos, Relatório de indisponibilidade dos serviços, Relatórios de desempenho e integridade de banco de dados, Relatórios de execução e qualidade de testes, Relatórios gerenciais de acompanhamento de projetos, Relatórios da solução de gestão de TIC, Relatórios gerenciais da solução de gestão de projetos, Relatórios de disponibilidade e consumo das integrações e dashboards (títulos adaptados ao edital).
- Todo dia: abertura, relatório diário e fechamento (Word).
- Por módulo: 15 evidências obrigatórias (escopo, requisitos, arquitetura, código alterado, commits, testes, logs, segurança, preview, capturas, revisões, responsáveis, medição, implantação, aceite).
- Checklist de 100 controles antes de cada entrega.

## 14. Riscos

- Nenhum risco registrado.

## 15. Comunicação e controle de mudanças

- Canal com o órgão: gestor/fiscal do contrato. Relatórios diários e mensais em Word.
- Mudança de escopo = registro de decisão + nova linha no planejamento + aprovação humana + aditivo quando o contrato exigir.

## 16. ESTIMATIVA × EXECUÇÃO REAL

| Medida | Planejado (ESTIMATIVA) | Comprovado (REAL) | Aceito (REAL) |
|---|---|---|---|
| UST – Unidade de Serviço Técnico, 'métrica que representa o esforço necessário à execução das atividades previstas' | — | 0 | 0 |
| Saldo do contrato | — | 325000 (projetado) | 325000 (oficial) |

## 17. Pendências para completar este GEC

- Formulário do contrato completo
- Documento base (empresa e capacidades)
- Seu planejamento preenchido (aba PLANEJAMENTO)
- Plano por projeto consolidado
- Ordem de serviço criada
- OS autorizada por quem pode autorizar
- Abertura do dia 2026-11-06
- Relatório diário 2026-11-06
- Fechamento do dia 2026-11-06

---
Aprovação humana do GEC: **pendente** (responsável técnico e gestor do contrato).
