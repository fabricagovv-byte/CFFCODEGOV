# Verificação das stacks

Executado em 2026-11-03T01:07:02-03:00 por `fabrica.py stacks verificar` (instala dependências e roda os testes de cada esqueleto).

| Stack | Linguagem | Situação | Verificações (instalar + testes + build) | Detalhe |
|---|---|---|---|---|
| dotnet-aspnet | C# (.NET 8) | NAO_VERIFICADO | — (— falhas) | ferramenta ausente: dotnet |
| go-http | Go 1.22+ | APROVADO | 2 (0 falhas) | go-http-testes: saída 0; go-http-build: saída 0 |
| java-spring | Java 21 | APROVADO | 3 (0 falhas) | java-spring-instalar: saída 0; java-spring-testes: saída 0; java-spring-build: saída 0 |
| node-typescript | TypeScript 5 (Node.js 22) | APROVADO | 2 (0 falhas) | node-typescript-instalar: saída 0; node-typescript-testes: saída 0; node-typescript-build: saída 0 |
| php-puro | PHP 8.2+ | NAO_VERIFICADO | — (— falhas) | não executado nesta máquina: o proxy deste ambiente bloqueia downloads do GitHub (HTTP 403) |
| python-fastapi | Python 3.12+ | APROVADO | 2 (0 falhas) | python-fastapi-instalar: saída 0; python-fastapi-testes: saída 0 |
| react-vite | TypeScript 5 (React 19) | APROVADO | 3 (0 falhas) | react-vite-instalar: saída 0; react-vite-testes: saída 0; react-vite-build: saída 0 |
| rust-std | Rust 1.80+ | APROVADO | 2 (0 falhas) | rust-std-testes: saída 0; rust-std-build: saída 0 |
| sistema-gov | Python 3.12+ e TypeScript (sistema completo) | APROVADO | 70 (0 falhas) | sistema-gov-instalar: saída 0; sistema-gov-testes: saída 0; sistema-gov-build: saída 0 |

NAO_VERIFICADO = o esqueleto existe, mas não foi executado nesta máquina (motivo na coluna Detalhe). Rode `fabrica.py stacks verificar <stack>` onde a ferramenta estiver disponível.
Logs: `fabrica/stacks/_verificacao/<stack>/`.
