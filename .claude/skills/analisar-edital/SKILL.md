---
name: analisar-edital
description: Leitura técnica de edital/TR/contrato para extrair serviços, quantidades, critérios de medição (UST/PF/horas), SLAs, glosas, exigências de equipe, tecnologias, segurança e aceite, com citação da cláusula. Use dentro de NOVO CONTRATO ou quando o usuário pedir para entender um edital.
---
# Analisar edital (G02)

Produza, em `contratos/<ID>/MATRIZ_RASTREABILIDADE.md` e num resumo ao usuário:

1. **Objeto e regime** — objeto, modalidade, lei aplicável (14.133/2021 ou regime anterior), vigência, valor.
2. **Catálogo de serviços** — cada item com código, descrição, unidade (UST/PF/hora/entregável), quantidade, complexidade, fórmula de cálculo e cláusula.
3. **Medição** — como se mede, quem atesta, prazos de aceite, regra de medição parcial, glosas/SLAs (indicador, meta, fórmula, desconto).
4. **Equipe** — perfis exigidos, qualificações, certificações, dedicação, preposto. Compare com `PROFISSIONAIS.csv`.
5. **Técnico** — tecnologias obrigatórias/vedadas, ambientes, integrações, segurança (LGPD, ISO 27001/27002, OWASP), acessibilidade (eMAG/WCAG).
6. **Entregáveis e aceite** — documentos e artefatos por OS, critério de aceite, termo provisório/definitivo.
7. **Riscos e conflitos** — ambiguidades e divergências entre documentos, para análise humana/jurídica.

Regras: toda afirmação cita documento + cláusula/página; o que não estiver escrito vira "não encontrado — perguntar ao usuário". Não estime valores que o edital não traz.
