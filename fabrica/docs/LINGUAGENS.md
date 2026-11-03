# Linguagens e tecnologias

A tecnologia é escolhida pelo **contrato**. Se o TR obrigar uma stack, ela prevalece. Sem exigência, a fábrica usa o padrão abaixo.

## Padrão da fábrica (usado no TESTE-001)

| Camada | Escolha | Por quê |
|---|---|---|
| Backend | Python 3.13 + FastAPI + SQLAlchemy 2 + Alembic | aberto, produtivo, OpenAPI automática |
| Frontend | TypeScript + React + Vite | tipagem, ecossistema, acessibilidade |
| Banco | PostgreSQL 16 | livre, robusto, comum em governo |
| Infra | Docker Compose; Nginx com TLS; GitHub Actions | portátil para nuvem ou datacenter do órgão |
| Testes | pytest; Vitest + Testing Library; Playwright (capturas/E2E) | rodam no CI e geram JUnit |

## Outras stacks que os agentes atendem quando o contrato pedir

| Linguagem | Frameworks comuns em contratos públicos | Testes |
|---|---|---|
| Java 17/21 | Spring Boot, Quarkus, JSF legado | JUnit 5, Testcontainers |
| C# / .NET 8 | ASP.NET Core, Entity Framework | xUnit/NUnit |
| PHP 8 | Laravel, Symfony | PHPUnit |
| JavaScript/TypeScript (Node) | NestJS, Express, Next.js | Jest/Vitest |
| Python | Django, FastAPI, Flask | pytest |
| Go | net/http, Gin | go test |
| Kotlin / Dart | Android, Flutter (apps) | JUnit, flutter test |
| SQL | PostgreSQL, Oracle, SQL Server, MySQL | testes de migração |
| Front legado | Angular, Vue | Karma/Jest/Vitest |

Regras: versão LTS suportada; dependências fixadas; teste automatizado em qualquer stack; o `fabrica.py testes executar` aceita qualquer comando de teste que gere JUnit XML (ou `tipo: comando` para checagens por código de saída).
