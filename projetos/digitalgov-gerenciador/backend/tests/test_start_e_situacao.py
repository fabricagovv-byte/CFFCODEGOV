import json
import os
import subprocess

import httpx

from app.servicos import situacao


def _servico_falso(monkeypatch, start_status=200):
    """Simula o serviço do projeto respondendo /health e /api/gerenciador/start."""
    chamadas = []

    def responder(req: httpx.Request) -> httpx.Response:
        chamadas.append((req.method, req.url.path, req.headers.get("authorization")))
        if req.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if req.url.path == "/api/gerenciador/start":
            return httpx.Response(start_status, json={"mensagem": "Ciclo de produção registrado no projeto"})
        return httpx.Response(404)
    monkeypatch.setattr(situacao, "cliente_http", lambda: httpx.Client(transport=httpx.MockTransport(responder)))
    return chamadas


def test_start_bloqueia_sem_contrato_e_sem_os_autorizada(cliente, base):
    h, ct = base["h"], base["contrato"]
    solto = cliente.post("/api/projetos", headers=h, json={"codigo": "solto", "nome": "Sem contrato"}).json()
    r = cliente.post(f"/api/projetos/{solto['id']}/start", headers=h).json()
    assert r["resultado"] == "BLOQUEADO" and any("sem contrato" in e["mensagem"] for e in r["etapas"])
    os2 = cliente.post("/api/ordens-servico", headers=h, json={"contrato_id": ct["id"], "numero": "OS-2", "descricao": "Não autorizada"}).json()
    pj = cliente.post("/api/projetos", headers=h, json={"codigo": "sem-autorizacao", "nome": "Projeto P", "contrato_id": ct["id"], "os_id": os2["id"]}).json()
    r = cliente.post(f"/api/projetos/{pj['id']}/start", headers=h).json()
    assert r["resultado"] == "BLOQUEADO" and any("sem autorização" in e["mensagem"] for e in r["etapas"])


def test_start_bloqueia_sem_banco_configurado(cliente, base):
    r = cliente.post(f"/api/projetos/{base['projeto']['id']}/start", headers=base["h"]).json()
    etapas = {e["etapa"]: e for e in r["etapas"]}
    assert r["resultado"] == "BLOQUEADO" and etapas["Banco de dados do projeto"]["situacao"] == "BLOQUEADO"
    assert etapas["Agentes (Codex)"]["mensagem"] == "Integração pendente"


def test_start_completo_inicia_o_servico_e_mostra_integracao_pendente(cliente, base, monkeypatch):
    h, pj = base["h"], base["projeto"]
    monkeypatch.setenv("PROJ_TESTE_DATABASE_URL", os.environ["TEST_DATABASE_URL"])
    monkeypatch.setenv("PROJ_TESTE_TOKEN", "token-do-projeto-para-teste")
    cliente.patch(f"/api/projetos/{pj['id']}", headers=h, json={"variavel_banco": "PROJ_TESTE_DATABASE_URL", "variavel_token": "PROJ_TESTE_TOKEN",
                                                               "url_servico": "http://projeto.local:9000"})
    chamadas = _servico_falso(monkeypatch)
    r = cliente.post(f"/api/projetos/{pj['id']}/start", headers=h).json()
    assert r["resultado"] == "INICIADO_SEM_AGENTES", r
    etapas = {e["etapa"]: e for e in r["etapas"]}
    assert etapas["Banco de dados do projeto"]["situacao"] == "OK" and "0001" in etapas["Banco de dados do projeto"]["mensagem"]
    assert etapas["Início da produção"]["mensagem"] == "Ciclo de produção registrado no projeto"
    assert etapas["Agentes (Codex)"]["mensagem"] == "Integração pendente"
    assert ("POST", "/api/gerenciador/start", "Bearer token-do-projeto-para-teste") in chamadas
    historico = cliente.get(f"/api/projetos/{pj['id']}/starts", headers=h).json()
    assert historico[0]["resultado"] == "INICIADO_SEM_AGENTES"
    assert "token-do-projeto" not in json.dumps(historico) and "senha" not in json.dumps(historico)


def test_situacao_nao_mostra_senha_do_banco(cliente, base, monkeypatch):
    h, pj = base["h"], base["projeto"]
    monkeypatch.setenv("PROJ_RUIM_DATABASE_URL", "postgresql+psycopg://usuario:SenhaSecreta@127.0.0.1:1/nada")
    cliente.patch(f"/api/projetos/{pj['id']}", headers=h, json={"variavel_banco": "PROJ_RUIM_DATABASE_URL"})
    r = cliente.get(f"/api/projetos/{pj['id']}/situacao", headers=h)
    assert r.json()["banco"]["situacao"] == "ERRO" and "SenhaSecreta" not in r.text
    assert r.json()["agentes"] == "Integração pendente"


def test_situacao_do_codigo_pelo_git(cliente, base, tmp_path, monkeypatch):
    h, pj = base["h"], base["projeto"]
    pasta = tmp_path / "meu-projeto"
    pasta.mkdir()
    (pasta / "a.txt").write_text("x")
    for cmd in (["git", "init", "-q"], ["git", "-c", "user.email=t@t", "-c", "user.name=T", "add", "."],
                ["git", "-c", "user.email=t@t", "-c", "user.name=T", "commit", "-qm", "primeira versão"]):
        subprocess.run(cmd, cwd=pasta, check=True)
    monkeypatch.setenv("GERENCIADOR_PROJETOS_DIR", str(tmp_path))
    cliente.patch(f"/api/projetos/{pj['id']}", headers=h, json={"pasta": "meu-projeto"})
    codigo = cliente.get(f"/api/projetos/{pj['id']}/situacao", headers=h).json()["codigo"]
    assert codigo["situacao"] == "OK" and codigo["mensagem"] == "primeira versão"


def test_importar_resultado_dos_testes(cliente, base):
    h, pj = base["h"], base["projeto"]
    xml = b'<testsuite><testcase name="a"/><testcase name="b"><failure/></testcase><testcase name="c"><skipped/></testcase></testsuite>'
    r = cliente.post(f"/api/projetos/{pj['id']}/testes", headers=h, files={"arquivo": ("junit.xml", xml, "application/xml")})
    assert r.status_code == 201 and (r.json()["total"], r.json()["falhas"], r.json()["ignorados"]) == (3, 1, 1)
    assert cliente.post(f"/api/projetos/{pj['id']}/testes", headers=h, files={"arquivo": ("x.xml", b"nao e xml", "application/xml")}).status_code == 422
