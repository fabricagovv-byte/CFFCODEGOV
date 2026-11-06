def test_cadastro_completo_e_filtro(cliente, base):
    h, ct = base["h"], base["contrato"]
    assert cliente.get(f"/api/ordens-servico?contrato_id={ct['id']}", headers=h).json()[0]["numero"] == "OS-1"
    assert cliente.get("/api/ordens-servico?contrato_id=999", headers=h).json() == []
    r = cliente.patch(f"/api/contratos/{ct['id']}", headers=h, json={"situacao": "SUSPENSO"})
    assert r.status_code == 200 and r.json()["situacao"] == "SUSPENSO"


def test_validacoes_do_contrato(cliente, base):
    h, org = base["h"], base["orgao"]
    vig = {"orgao_id": org["id"], "numero": "X", "objeto": "Obj", "metrica": "UST", "vigencia_inicio": "2026-12-01", "vigencia_fim": "2026-01-01"}
    assert cliente.post("/api/contratos", headers=h, json=vig).status_code == 422
    outra = {"orgao_id": org["id"], "numero": "Y", "objeto": "Obj", "metrica": "OUTRA"}
    assert cliente.post("/api/contratos", headers=h, json=outra).status_code == 422
    dup = {"orgao_id": org["id"], "numero": "12/2026", "objeto": "Obj", "metrica": "UST"}
    assert cliente.post("/api/contratos", headers=h, json=dup).status_code == 409


def test_alteracao_parcial_respeita_as_regras(cliente, base):
    h, ct = base["h"], base["contrato"]
    assert cliente.patch(f"/api/contratos/{ct['id']}", headers=h, json={"vigencia_fim": "2020-01-01"}).status_code == 422


def test_os_autorizada_precisa_de_responsavel(cliente, base):
    h, ct = base["h"], base["contrato"]
    r = cliente.post("/api/ordens-servico", headers=h, json={"contrato_id": ct["id"], "numero": "OS-2", "descricao": "Sem autor", "autorizada": True})
    assert r.status_code == 422


def test_relacionamento_inexistente_responde_409(cliente, base):
    r = cliente.post("/api/contratos", headers=base["h"], json={"orgao_id": 999, "numero": "Z", "objeto": "Obj", "metrica": "UST"})
    assert r.status_code == 409 and "relacionado" in r.json()["detail"]


def test_projeto_guarda_so_o_nome_da_variavel_do_banco(cliente, base):
    h = base["h"]
    ok = {"codigo": "proj-dois", "nome": "Dois", "variavel_banco": "PROJ_DOIS_DATABASE_URL"}
    assert cliente.post("/api/projetos", headers=h, json=ok).status_code == 201
    senha_no_campo = {"codigo": "proj-tres", "nome": "Três", "variavel_banco": "postgresql://u:senha@host/db"}
    assert cliente.post("/api/projetos", headers=h, json=senha_no_campo).status_code == 422
    assert cliente.post("/api/projetos", headers=h, json={"codigo": "X", "nome": "Ruim"}).status_code == 422
    assert cliente.post("/api/projetos", headers=h, json={"codigo": "proj-quatro", "nome": "Q", "pasta": "../fora"}).status_code == 422


def test_profissional_so_com_cpf_mascarado(cliente, base):
    h = base["h"]
    assert cliente.post("/api/profissionais", headers=h, json={"nome": "Ana", "cargo": "Programadora", "cpf_mascarado": "123.456.789-00"}).status_code == 422
    assert cliente.post("/api/profissionais", headers=h, json={"nome": "Ana", "cargo": "Programadora", "cpf_mascarado": "***.456.789-**"}).status_code == 201


def test_agente_tarefa_evidencia(cliente, base):
    h, pj = base["h"], base["projeto"]
    ag = cliente.post("/api/agentes", headers=h, json={"codigo": "E05", "nome": "Desenvolvedor Backend I", "projeto_id": pj["id"]}).json()
    assert ag["situacao"] == "INTEGRACAO_PENDENTE"
    t = cliente.post("/api/tarefas", headers=h, json={"projeto_id": pj["id"], "titulo": "Criar cadastro", "agente_id": ag["id"]}).json()
    ev = cliente.post("/api/evidencias", headers=h, json={"projeto_id": pj["id"], "tarefa_id": t["id"], "tipo": "COMMIT", "descricao": "Commit do cadastro", "referencia": "abc1234"})
    assert ev.status_code == 201
    assert cliente.get(f"/api/tarefas?projeto_id={pj['id']}", headers=h).json()[0]["titulo"] == "Criar cadastro"


def test_medicao_aceita_precisa_de_documento(cliente, base):
    h, ct = base["h"], base["contrato"]
    m = {"contrato_id": ct["id"], "item": "M01", "descricao": "Entrega", "quantidade": 10, "data_execucao": "2026-11-06", "situacao": "ACEITA"}
    assert cliente.post("/api/medicoes", headers=h, json=m).status_code == 422
    assert cliente.post("/api/medicoes", headers=h, json={**m, "documento_aceite": "Termo 1/2026"}).status_code == 201


def test_resumo_da_medicao_do_contrato(cliente, base):
    h, ct = base["h"], base["contrato"]
    base_item = {"contrato_id": ct["id"], "descricao": "Entrega", "data_execucao": "2026-11-06"}
    cliente.post("/api/medicoes", headers=h, json={**base_item, "item": "A", "quantidade": 202.5})
    cliente.post("/api/medicoes", headers=h, json={**base_item, "item": "B", "quantidade": 100, "situacao": "ACEITA", "documento_aceite": "Termo"})
    r = cliente.get(f"/api/contratos/{ct['id']}/medicao", headers=h).json()
    assert (r["executado"], r["aceito"], r["saldo"], r["valor_executado"], r["valor_aceito"]) == (302.5, 100, 697.5, 9075.0, 3000.0)


def test_auditoria_registra_antes_e_depois(cliente, base):
    from app.db import _fabrica_sessoes
    from app.modelos import Auditoria
    h, ct = base["h"], base["contrato"]
    cliente.patch(f"/api/contratos/{ct['id']}", headers=h, json={"objeto": "Novo objeto"})
    with _fabrica_sessoes()() as s:
        ultimo = s.query(Auditoria).filter_by(acao="ALTERAR", entidade="contratos").one()
        assert "Sistema de teste" in ultimo.detalhe and "Novo objeto" in ultimo.detalhe
