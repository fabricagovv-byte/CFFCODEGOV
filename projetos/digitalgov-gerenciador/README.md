# Gerenciador Central DigitalGov

Painel e API que reúnem contratos, OS, projetos, equipe, horas manuais, evidências, medição e relatórios.
Somente leitura no painel; os lançamentos entram pela API autenticada. Dados reais ficam no PostgreSQL deste gerenciador.

## Operar (máquina local)

1. Banco e usuário próprios (senha em arquivo fora do repositório, permissão 600):
   ```bash
   sudo -u postgres psql -c "CREATE ROLE gerenciador_app LOGIN PASSWORD 'SENHA';"
   sudo -u postgres psql -c "CREATE DATABASE digitalgov_gerenciador OWNER gerenciador_app;"
   ```
2. Variáveis (copie `.env.example` para `.env`, fora do git): `GERENCIADOR_DATABASE_URL`, `GERENCIADOR_ARQUIVOS`.
3. Migrações: `cd backend && python3 -m alembic upgrade head`.
4. Primeiro administrador (só funciona com o banco vazio; a senha é digitada sem eco):
   `python3 -m app.bootstrap --login admin --nome "Administrador"`.
5. Servidor: `python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8200` → painel em `http://127.0.0.1:8200/`.

## Testes

`cd backend && TEST_DATABASE_URL=postgresql+psycopg://usuario:senha@127.0.0.1:5432/banco_de_teste python3 -m pytest -q`
(o banco de teste é apagado a cada teste; nunca aponte para o banco real).

## Limites conhecidos

- O painel mostra indicadores, contratos e últimos starts. Telas de cadastro, lançamento de horas e medição ainda são só API.
- Agentes de IA aparecem como "integração pendente": não há conector de execução ligado a este gerenciador.
- Não há implantação em servidor do órgão nem backup automático configurado.
