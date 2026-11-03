"""Testes da CLI da fábrica. Cada teste roda num repositório git temporário."""
from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ORIGEM = Path(__file__).resolve().parents[3]


@pytest.fixture
def fab(tmp_path, monkeypatch):
    raiz = tmp_path / "repo"
    for sub in ("fabrica/agentes", "fabrica/qualidade", "fabrica/templates"):
        shutil.copytree(ORIGEM / sub, raiz / sub)
    (raiz / "fabrica/comunicacao").mkdir(parents=True)
    (raiz / "fabrica/comunicacao/AGENT_TASKS.json").write_text('{"versao": 1, "tarefas": []}')
    subprocess.run(["git", "init", "-q"], cwd=raiz, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=raiz, check=True)
    subprocess.run(["git", "config", "user.name", "Teste"], cwd=raiz, check=True)
    monkeypatch.setenv("FABRICA_RAIZ", str(raiz))
    sys.path.insert(0, str(ORIGEM / "fabrica/ferramentas"))
    mod = importlib.reload(importlib.import_module("fabrica"))
    yield mod
    sys.path.remove(str(ORIGEM / "fabrica/ferramentas"))


def test_registro_tem_40_agentes_e_gera_arquivos(fab):
    assert len(fab.gerar_agentes()) == 40
    assert fab.verificar_agentes() == []


def test_checklist_tem_100_controles_unicos(fab):
    ck = yaml.safe_load((fab.FAB / "qualidade/checklist_100.yaml").read_text())
    ids = [c["id"] for g in ck["grupos"] for c in g["controles"]]
    assert len(ck["grupos"]) == 10 and all(len(g["controles"]) == 10 for g in ck["grupos"])
    assert len(ids) == len(set(ids)) == 100


def test_maquina_de_estados(fab):
    t = fab.criar_tarefa(agente="G06", descricao="API")
    with pytest.raises(fab.ErroFabrica, match="transição não permitida"):
        fab.mover_tarefa(t["id"], "DONE", por="G06")
    for s in ("READY", "IN_PROGRESS", "IN_REVIEW", "TESTING"):
        fab.mover_tarefa(t["id"], s, por="G06")
    with pytest.raises(fab.ErroFabrica, match="exige --resultado"):
        fab.mover_tarefa(t["id"], "DONE", por="G06")
    with pytest.raises(fab.ErroFabrica, match="não encontradas"):
        fab.mover_tarefa(t["id"], "DONE", por="G06", resultado="ok", evidencias=["nao/existe.md"])
    (fab.RAIZ / "prova.md").write_text("x")
    assert fab.mover_tarefa(t["id"], "DONE", por="G06", resultado="ok", evidencias=["prova.md"])["status"] == "DONE"
    assert fab.validar_quadro() == []


def test_dependencias_e_conflito_de_arquivos(fab):
    a = fab.criar_tarefa(agente="G06", descricao="A", arquivos=["backend/app/x.py"])
    b = fab.criar_tarefa(agente="G07", descricao="B", dependencias=[a["id"]])
    c = fab.criar_tarefa(agente="G08", descricao="C", arquivos=["backend/app"])
    for t in (a, b, c):
        fab.mover_tarefa(t["id"], "READY", por="G14")
    with pytest.raises(fab.ErroFabrica, match="dependências"):
        fab.mover_tarefa(b["id"], "IN_PROGRESS", por="G07")
    fab.mover_tarefa(a["id"], "IN_PROGRESS", por="G06")
    with pytest.raises(fab.ErroFabrica, match="conflito de arquivos"):
        fab.mover_tarefa(c["id"], "IN_PROGRESS", por="G08")


def test_bloqueio_exige_motivo_e_agente_valido(fab):
    t = fab.criar_tarefa(agente="E05", descricao="X")
    with pytest.raises(fab.ErroFabrica, match="motivo"):
        fab.mover_tarefa(t["id"], "BLOCKED", por="E05")
    with pytest.raises(fab.ErroFabrica, match="agente inexistente"):
        fab.criar_tarefa(agente="Z99", descricao="X")


def test_formulario_lista_campos_faltantes(fab):
    fab.novo_contrato("C1")
    faltam = fab.campos_faltantes("C1")
    assert "contratante.orgao" in faltam and "contrato.numero" in faltam


def _os_minima(fab, cid="C1"):
    proj = fab.RAIZ / "proj"
    proj.mkdir()
    (proj / "a.py").write_text("print(1)\n")
    subprocess.run(["git", "add", "."], cwd=fab.RAIZ, check=True)
    subprocess.run(["git", "commit", "-qm", "inicial"], cwd=fab.RAIZ, check=True)
    d = fab.CONTRATOS / cid
    (d / "TABELA_UST.csv").write_text("codigo,descricao,unidade,ust_por_unidade,complexidade,referencia_contratual,observacao\nIT1,Item,UST,1,MEDIA,TR 1,\n")
    (d / "os/OS1.yaml").write_text(yaml.safe_dump({
        "os": "OS1", "contrato": cid, "projeto": "proj",
        "autorizacao": {"autorizado": True, "autorizado_por": "teste", "data": "2026-01-01"},
        "modulos": [{"id": "M1", "nome": "Mod", "item_tabela": "IT1", "ust_previsto": 3, "caminhos": ["a.py"],
                     "testes": [{"nome": "ok", "tipo": "comando", "cwd": ".", "cmd": ["true"]}]}]}))


def test_medicao_so_comprova_com_evidencia_completa_e_aceite_humano(fab):
    fab.novo_contrato("C1")
    _os_minima(fab)
    fab.preparar_evidencias("C1", "OS1")
    m = fab.medir("C1", "OS1")["itens"][0]
    assert (m["previsto"], m["comprovado"], m["aceito"]) == (3, 0, 0)  # modelos sem preencher, sem testes
    d = fab.dir_mod("C1", "OS1", "M1")
    for f in d.glob("*.md"):
        f.write_text(f.read_text().replace("<PREENCHER>", "preenchido"))
    fab.coletar_commits("C1", "OS1")
    fab.executar_testes("C1", "OS1")
    m = fab.medir("C1", "OS1")["itens"][0]
    assert (m["comprovado"], m["aceito"]) == (3, 0)
    (d / "ACEITE.md").write_text("---\nstatus: ACEITO\nquantidade_aceita: 5\naceito_por: Fiscal X\ndocumento: Termo 1\n---\n")
    assert fab.medir("C1", "OS1")["itens"][0]["aceito"] == 3  # nunca maior que o comprovado


def test_os_sem_autorizacao_nao_executa(fab):
    fab.novo_contrato("C1")
    _os_minima(fab)
    p = fab.CONTRATOS / "C1/os/OS1.yaml"
    o = yaml.safe_load(p.read_text()); o["autorizacao"]["autorizado"] = False
    p.write_text(yaml.safe_dump(o))
    with pytest.raises(fab.ErroFabrica, match="sem autorização"):
        fab.executar_testes("C1", "OS1")


def test_commit_inventado_reprova_auditoria(fab):
    fab.novo_contrato("C1")
    _os_minima(fab)
    fab.preparar_evidencias("C1", "OS1")
    d = fab.dir_mod("C1", "OS1", "M1")
    (d / "COMMITS.json").write_text(json.dumps({"commits": [{"sha": "f" * 40}]}))
    achados = fab.auditar("C1", "OS1")["modulos"][0]["achados"]
    assert any("commit inexistente" in a["texto"] for a in achados)


def test_participacao_sem_evidencia_e_rejeitada(fab):
    fab.novo_contrato("C1")
    d = fab.CONTRATOS / "C1"
    (d / "PROFISSIONAIS.csv").write_text("id,nome,funcao,qualificacao,registro_ou_certificacao,responsabilidades,modulos,email_corporativo,inicio,fim\nP1,Fulana,Dev,,,,,,,\n")
    (d / "PARTICIPACOES.csv").write_text("data,profissional_id,os,modulo,tipo,descricao,evidencia,horas_declaradas\n"
                                         "2026-01-02,P1,OS1,M1,REVISAO,revisou,,\n2026-01-02,P9,OS1,M1,REVISAO,x,PR 1,\n"
                                         "2026-01-02,P1,OS1,M1,APROVACAO,aprovou,PR 2,\n")
    validas, erros = fab.carregar_participacoes("C1")
    assert len(validas) == 1 and len(erros) == 2


def test_estatisticas_producao(fab, tmp_path):
    arq = tmp_path / "hist.csv"
    arq.write_text("profissional,mes,os,item_tabela,complexidade,ust_aceita,documento_aceite\n"
                   "P1,2026-09,OS1,X,ALTA,20,T1\nP1,2026-10,OS2,X,ALTA,30,T2\nP1,2026-10,OS3,X,BAIXA,4,T3\n")
    linhas = {(l["profissional"], l["complexidade"]): l for l in fab.estatisticas_producao(arq)["linhas"]}
    assert linhas[("P1", "ALTA")]["media_ust_por_os"] == 25 and linhas[("P1", "BAIXA")]["os_registradas"] == 1


def test_mascara_credenciais(fab):
    assert fab.mascarar("postgresql://u:segredo@h:5432/db") == "postgresql://u:***@h:5432/db"
