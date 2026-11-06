# Roteiro de conferência — OS-FIC-002

Contrato FIC-COM-2026-001 · Plataforma de Comunicação Institucional · 06/11/2026

O checklist de 100 controles da OS-FIC-002 está assim: 39 aprovados automaticamente, 1 reprovado (não crítico) e 60 que dependem de conferência humana. Destes, 18 são críticos e precisam ser conferidos antes de liberar o pacote de entrega. A coluna "O que a fábrica encontrou" é o resultado preparado pela fábrica; a decisão é de quem confere.

## Controles críticos para conferir

| Controle | O que a fábrica encontrou | Onde ver | Conferido (Sim/Não) |
|---|---|---|---|
| **C003** · OS autorizada por responsável do contratante | Autorização interna da contratada em 06/11/2026. A OS do órgão ainda não foi recebida | `os/OS-FIC-002.yaml` | |
| **C009** · Equipe exigida pelo edital × equipe cadastrada | 7 programadores cadastrados. O edital do órgão ainda não foi recebido para comparar | `PROFISSIONAIS.csv` | |
| **C012** · Tecnologias compatíveis com o contrato | Python/FastAPI, banco relacional SQLite com migrações, telas HTML/JavaScript; atende à arquitetura do TR (seção 2). Decidir se a produção usa SQLite ou PostgreSQL | `laboratorio/README.md` | |
| **C024** · Validação de entradas em todas as APIs | Todas as entradas passam por `app/esquemas.py`; testes de dado inválido devolvem 422 | `app/esquemas.py`, testes MOD-002 | |
| **C032** · Migração aplicada em banco real | Migrações 0001 a 0003 aplicadas e desfeitas pela linha de comando em banco vazio | Log `migracoes-ida-e-volta` do MOD-003 | |
| **C037** · Restauração testada | Backup, perda simulada e restauração conferida; arquivo alterado é recusado | `tests/test_backup.py`, log do MOD-003 | |
| **C039** · Dados de demonstração fictícios | Usuários DEMO só nos testes; o banco de produção nasce vazio | `tests/conftest.py`, `app/cli.py` | |
| **C041** · Autenticação implementada e testada | Login, sessão no servidor, saída e bloqueio após 5 erros; 9 testes | `tests/test_mod001_sessao.py` | |
| **C042** · Autorização por perfil (menor privilégio) | Quatro perfis; leitor não cria, não vê contatos nem descrição de chamados (testes 403) | `app/acesso.py`, testes MOD-002 | |
| **C043** · Senhas com hash forte | PBKDF2-SHA256 com 260.000 iterações e sal aleatório. O controle cita bcrypt/argon2: decidir se aceita PBKDF2 ou pede troca | `app/security.py` | |
| **C045** · Trilha de auditoria de ações sensíveis | Login certo, errado, bloqueado, saída, criação, aprovação e publicação registrados | Tela Auditoria, testes MOD-001 | |
| **C047** · TLS em homologação e produção | Nginx com TLS 1.2/1.3, HTTP→HTTPS e HSTS configurado; ainda não publicado | `infra/nginx/prod-tls.conf` | |
| **C051** · Testes de back-end sem falhas | 97 verificações aprovadas, 0 falhas | `evidencias/OS-FIC-002/*/TESTES.json` | |
| **C052** · Testes de front-end sem falhas | Não há testes unitários de tela em formato JUnit; as telas foram conferidas no navegador com capturas, sem erro de JavaScript | `evidencias/.../SCREENSHOTS/` | |
| **C062** · Limite de tamanho de envio | A plataforma não tem envio de arquivos; o Nginx limita requisições a 2 MB. Pode ser marcado "não se aplica" | `infra/nginx/default.conf` | |
| **C087** · Nenhuma equivalência UST/PF/horas inventada | Medição só pelo catálogo (UST base × fator ÷ entregas); horas não viram UST | `medicoes/OS-FIC-002.md` | |
| **C090** · Participação humana com origem registrada | Pendente: documento de participação ainda não preenchido | `PARTICIPACAO_EQUIPE_FIC-COM-2026-001.docx` | |
| **C099** · Aprovação humana técnica registrada | Pendente: aguarda a aprovação de quem confere este roteiro | `RESPONSAVEIS.md`, `REVISOES.md` | |

## Controle reprovado (não crítico)

| Controle | Motivo |
|---|---|
| **C026** · Tipagem aplicada | O back-end tem tipagem completa; o front-end é JavaScript sem tipagem (não usa TypeScript). Corrigir exige reescrever as telas em TypeScript |

## Depois de conferir

Responda com os números conferidos e quem conferiu (nome e cargo), por exemplo: "Conferi todos, Warley Luciano Costa Gomes, Gerente Geral". A fábrica registra a conferência e gera o pacote de entrega da OS.
