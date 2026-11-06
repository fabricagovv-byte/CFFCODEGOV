from datetime import date, timedelta


def _pessoa(cliente, h, nome="Jerlian", ativo=True):
    return cliente.post("/api/profissionais", headers=h, json={"nome": nome, "cargo": "Programador", "ativo": ativo}).json()["id"]


def _lancar(cliente, h, **campos):
    dados = {"tipo": "HUMANA", "data": "2026-11-04", "inicio": "09:00", "fim": "18:00", "intervalo_min": 60, "atividade": "Revisão de código"}
    dados.update(campos)
    return cliente.post("/api/horas", headers=h, json=dados)


def test_lancamento_calcula_horas_liquidas(cliente, base):
    h = base["h"]
    r = _lancar(cliente, h, profissional_id=_pessoa(cliente, h))
    assert r.status_code == 201 and r.json()["horas"] == 8.0


def test_regras_do_lancamento(cliente, base):
    h = base["h"]
    p = _pessoa(cliente, h)
    assert _lancar(cliente, h).status_code == 422                                          # humana sem profissional
    assert _lancar(cliente, h, tipo="IA", profissional_id=p).status_code == 422             # IA em nome de pessoa
    assert _lancar(cliente, h, profissional_id=p, inicio="18:00", fim="09:00").status_code == 422
    assert _lancar(cliente, h, profissional_id=p, inicio="09:00", fim="10:00", intervalo_min=60).status_code == 422


def test_totais_separam_humanas_aceitas_e_ia(cliente, base):
    h, pj = base["h"], base["projeto"]
    p = _pessoa(cliente, h)
    ag = cliente.post("/api/agentes", headers=h, json={"codigo": "E05", "nome": "Backend"}).json()["id"]
    l1 = _lancar(cliente, h, profissional_id=p).json()
    _lancar(cliente, h, profissional_id=p, data="2026-11-05", inicio="09:00", fim="13:00", intervalo_min=0)
    _lancar(cliente, h, tipo="IA", agente_id=ag, data="2026-11-05", inicio="20:00", fim="23:30", intervalo_min=0, atividade="Execução automatizada")
    assert cliente.post(f"/api/horas/{l1['id']}/aceite", headers=h, json={"aceito_por": "Fiscal", "documento": "Termo 3", "aceito_em": "2026-11-06"}).status_code == 201
    r = cliente.get("/api/horas/resumo?mes=2026-11", headers=h).json()
    assert r["total"] == {"humanas": 12.0, "aceitas": 8.0, "ia": 3.5}
    mes = {(x["tipo"], x["id"]): x for x in r["por_mes"]}
    assert mes[("profissional", p)]["humanas"] == 12.0 and mes[("agente", ag)]["ia"] == 3.5
    assert len([d for d in r["por_dia"] if d["tipo"] == "profissional"]) == 2


def test_inconsistencias_sao_apontadas_sem_alterar_lancamentos(cliente, base):
    h = base["h"]
    p = _pessoa(cliente, h)
    inativo = _pessoa(cliente, h, "Antigo", ativo=False)
    _lancar(cliente, h, profissional_id=p, data="2026-11-04", inicio="08:00", fim="14:00", intervalo_min=0)
    _lancar(cliente, h, profissional_id=p, data="2026-11-04", inicio="13:00", fim="19:00", intervalo_min=0)   # sobrepõe e passa de 8 h
    _lancar(cliente, h, profissional_id=p, data="2026-11-07", inicio="09:00", fim="11:00", intervalo_min=0)   # sábado
    futuro = (date.today() + timedelta(days=40)).isoformat()
    _lancar(cliente, h, profissional_id=p, data=futuro, inicio="09:00", fim="10:00", intervalo_min=0)
    _lancar(cliente, h, profissional_id=inativo, data="2026-11-04")
    antes = cliente.get("/api/horas", headers=h).json()
    tipos = {a["tipo"] for a in cliente.get("/api/horas/resumo", headers=h).json()["inconsistencias"]}
    assert {"SOBREPOSICAO", "ACIMA_DA_JORNADA", "FIM_DE_SEMANA", "DATA_FUTURA", "PROFISSIONAL_INATIVO"} <= tipos
    assert cliente.get("/api/horas", headers=h).json() == antes


def test_aceite_so_para_horas_humanas_e_trava_correcao(cliente, base):
    h = base["h"]
    p = _pessoa(cliente, h)
    ag = cliente.post("/api/agentes", headers=h, json={"codigo": "E06", "nome": "Backend II"}).json()["id"]
    ia = _lancar(cliente, h, tipo="IA", agente_id=ag, atividade="Execução automatizada").json()
    aceite = {"aceito_por": "Fiscal", "documento": "Termo", "aceito_em": "2026-11-06"}
    assert cliente.post(f"/api/horas/{ia['id']}/aceite", headers=h, json=aceite).status_code == 409
    hum = _lancar(cliente, h, profissional_id=p).json()
    cliente.post(f"/api/horas/{hum['id']}/aceite", headers=h, json=aceite)
    novo = {"tipo": "HUMANA", "profissional_id": p, "data": "2026-11-04", "inicio": "09:00", "fim": "12:00", "atividade": "Ajuste"}
    assert cliente.patch(f"/api/horas/{hum['id']}", headers=h, json=novo).status_code == 409
    assert cliente.delete(f"/api/horas/{hum['id']}", headers=h).status_code == 409
    assert cliente.delete(f"/api/horas/{hum['id']}/aceite", headers=h).status_code == 204
    assert cliente.patch(f"/api/horas/{hum['id']}", headers=h, json=novo).json()["horas"] == 3.0


def test_filtro_por_mes(cliente, base):
    h = base["h"]
    p = _pessoa(cliente, h)
    _lancar(cliente, h, profissional_id=p, data="2026-10-30")
    _lancar(cliente, h, profissional_id=p, data="2026-11-03")
    assert [l["data"] for l in cliente.get("/api/horas?mes=2026-11", headers=h).json()] == ["2026-11-03"]
    assert cliente.get("/api/horas?mes=11-2026", headers=h).status_code == 422
