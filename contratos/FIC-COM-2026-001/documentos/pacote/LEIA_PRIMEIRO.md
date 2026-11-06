# DIGITALGOV — PACOTE INTEGRADO DE FÁBRICA DE SOFTWARE E CONTRATO DE COMUNICAÇÃO

**Contrato FICTÍCIO** `FIC-COM-2026-001`: não assinado, não é edital real, não é vínculo com órgão federal. Estrutura formal inspirada em boas práticas de fiscalização de TIC, mas é necessária revisão jurídica e técnica antes de qualquer uso real.

## Pastas

- `DOCUMENTOS/`: contrato fictício, TR, OS proposta, medição, equipe, modelo de relatório, checklist, guia e prompt Word.
- `PLANILHAS/`: planejamento 12.000 UST ajustadas, por módulo e competência, sem confundir meta com execução.
- `FABRICA/`: Factory Control Center (FastAPI + SQLite); cadastro de OS, equipe, jornada, auditoria, medições e botão START para preparar prompts.
- `PLATAFORMA_COMUNICACAO/`: MVP com autenticação, canais, publicação, aprovações, campanhas, contatos, chamados e auditoria. Não é uma plataforma governamental homologada.
- `COMANDOS/`: prompt mestre e comando inicial de instalação.

## Instalação local (Linux/macOS)

```bash
python -m pip install -r FABRICA/requirements.txt
python -m pip install -r PLATAFORMA_COMUNICACAO/requirements.txt
export DG_COMM_SECRET=$(python -c 'import secrets; print(secrets.token_urlsafe(48))')
cd PLATAFORMA_COMUNICACAO
python -m app.cli init
python -m app.cli add-user --name Administrador --username admin --role ADMIN --password 'SENHA-FORTE-DE-TESTE-1234'
cd ..
./start_local.sh
```

Acesse `http://127.0.0.1:8777` (fábrica) e `http://127.0.0.1:8765` (comunicação). Não exponha o painel da fábrica, que neste pacote NÃO tem autenticação, à internet.

## Testes

```bash
(cd FABRICA && python -m pytest -q tests)
(cd PLATAFORMA_COMUNICACAO && python -m pytest -q tests)
```

## O que não está pronto

Integração real ao Codex/Valide, concorrência de 100 agentes, mensageria WebSocket, conectores de envio real e-mail/SMS/push, SSO, aplicação na infraestrutura do cliente, conformidade LGPD/auditoria imutável, homologação por órgão e implementação completa dos 18 módulos não estão concluídos. Todas as lacunas aparecem na documentação; o código já executável é um MVP de partida.

## Responsabilidade pela medição

O contrato fictício prevê 12.000 UST como teto de planejamento; as UST verificadas e homologadas começam em ZERO. Ordem e catálogo assinados por partes reais, fiscalização e aceite são necessários para serviços públicos reais. Profissionais reais não recebem automaticamente horas de IA.
