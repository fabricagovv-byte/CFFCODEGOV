# Decisões registradas

Registro gerado pela CLI (`fabrica.py decisao`). Não edite entradas antigas; acrescente novas.

## D-0001 — Stack do TESTE-001

- Data: 2026-11-02T23:09:46-03:00
- Registrado por: G05

Contexto: Parte 7 do prompt exige React + FastAPI + PostgreSQL.
Decisão: FastAPI/SQLAlchemy/Alembic, React/TS/Vite, PostgreSQL 16, Docker Compose, Nginx.
Consequência: padrão da fábrica quando o contrato não exigir outra stack (fabrica/docs/LINGUAGENS.md).

## D-0002 — Correções da revisão independente

- Data: 2026-11-02T23:09:46-03:00
- Registrado por: G01

Contexto: revisão G13/G10 em subagente separado.
Decisão: corrigir 1 ALTO, 5 MÉDIOS e os BAIXOS de baixo custo antes de registrar evidências; manter como risco residual o limitador em memória (Redis) e e-mail em falhas de login.
Consequência: migração 0002_versao_sessao; testes novos.

## D-0003 — Imagens base via espelho

- Data: 2026-11-02T23:09:46-03:00
- Registrado por: G11

Contexto: Docker Hub respondeu 429 (limite).
Decisão: nesta sessão as imagens base foram obtidas de mirror.gcr.io e re-etiquetadas; Dockerfiles continuam apontando para as imagens oficiais.
Consequência: em ambientes com o mesmo limite, usar espelho/cache de registro.

## D-0004 — FIC-COM-2026-001: respostas do responsável em 06/11/2026

- Data: 2026-11-06T14:19:17-03:00
- Registrado por: Responsável da sessão

- Tarefa: T-0030

Órgão contratante existe (nome e documentos a enviar). Autorização da OS: o próprio responsável. Catálogo PROPOSTO-V1 aprovado com UST a R$ 30,00. Equipe: 7 programadores (P01-P07). Corrigir os 12 achados e medir. Regra de medição parcial proposta pela fábrica aguarda confirmação.
