"""Testes da CLI da fábrica. Cada teste roda num repositório git temporário."""
from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import zipfile
import sys
from pathlib import Path

import pytest
import yaml

ORIGEM = Path(__file__).resolve().parents[3]


@pytest.fixture
def fab(tmp_path, monkeypatch):
    raiz = tmp_path / "repo"
    for sub in ("fabrica/agentes", "fabrica/qualidade", "fabrica/templates", "fabrica/stacks", "fabrica/modelos_repositorio",
                "fabrica/docs", "fabrica/legislacao", "fabrica/ferramentas", ".claude/skills", ".codex"):
        shutil.copytree(ORIGEM / sub, raiz / sub, ignore=shutil.ignore_patterns("__pycache__", "_verificacao", "tests"))
    for f in ("AGENTS.md", "CLAUDE.md", ".claude/settings.json"):
        shutil.copy2(ORIGEM / f, raiz / f)
    (raiz / "fabrica/comunicacao").mkdir(parents=True)
    (raiz / "fabrica/comunicacao/AGENT_TASKS.json").write_text('{"versao": 1, "tarefas": []}')
    subprocess.run(["git", "init", "-q"], cwd=raiz, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=raiz, check=True)
    subprocess.run(["git", "config", "user.name", "Teste"], cwd=raiz, check=True)
    monkeypatch.setenv("FABRICA_RAIZ", str(raiz))
    monkeypatch.setenv("FABRICA_WORD", "0")  # Word só nos testes específicos (mais rápido)
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


# ------------------------------------------------------------ equipe / rateio / modelo

CPF_OK = "529.982.247-25"  # CPF válido de exemplo (dígitos verificadores corretos), não pertence à equipe


def test_validacao_e_mascara_de_cpf(fab):
    assert fab.validar_cpf(CPF_OK) and not fab.validar_cpf("111.111.111-11") and not fab.validar_cpf("529.982.247-24")
    assert fab.mascarar_cpf(CPF_OK) == "***.982.247-**"


def _equipe(fab, tmp_path):
    fab.novo_contrato("C1")
    arq = tmp_path / "equipe.csv"
    arq.write_text("nome,funcao,cpf,area,senioridade\n"
                   f"Ana Sênior,Desenvolvedora Backend,{CPF_OK},BACKEND,SENIOR\n"
                   "Beto Júnior,Desenvolvedor Backend,,BACKEND,JUNIOR\n"
                   "Carla Plena,Desenvolvedora Frontend,,FRONTEND,PLENO\n"
                   "Dado Errado,Analista,123.456.789-00,DADOS,PLENO\n")
    return fab.importar_profissionais("C1", arq)


def test_importa_equipe_com_cpf_so_na_pasta_privada(fab, tmp_path):
    r = _equipe(fab, tmp_path)
    assert r["novos"] == 3 and any("CPF inválido" in e for e in r["erros"])
    d = fab.CONTRATOS / "C1"
    publico = (d / "PROFISSIONAIS.csv").read_text()
    assert "529.982.247-25" not in publico and "52998224725" not in publico and "***.982.247-**" in publico
    priv = d / "privado" / "PROFISSIONAIS_PRIVADO.csv"
    assert "52998224725" in priv.read_text() and oct(priv.stat().st_mode)[-3:] == "600"
    assert fab.importar_profissionais("C1", tmp_path / "equipe.csv")["novos"] == 0  # reimportar mantém IDs


def _participacoes(fab, linhas):
    (fab.CONTRATOS / "C1" / "PARTICIPACOES.csv").write_text(
        "data,profissional_id,os,modulo,tipo,descricao,evidencia,horas_declaradas\n" + "".join(l + "\n" for l in linhas))


def test_rateio_proporcional_de_250_ust(fab, tmp_path):
    _equipe(fab, tmp_path)
    _participacoes(fab, ["2026-11-03,P01,OS1,M1,REVISAO,revisou,PR 1,", "2026-11-04,P02,OS1,M1,CONDUCAO,fez,commit abc,",
                         "2026-11-05,P03,OS1,M2,CORRECAO,corrigiu,registro do gestor em 2026-11-05,",
                         "2026-10-01,P01,OS1,M1,CONDUCAO,fora do período,PR 0,"])
    r = fab.rateio("C1", "semanal", "2026-11-04", total=250)
    u = {l["profissional_id"]: l["ust"] for l in r["linhas"]}
    # pesos: P01 1*1.5=1.5 ; P02 3*0.7=2.1 ; P03 2*1.0=2 → soma 5.6
    assert u == {"P01": round(250 * 1.5 / 5.6, 2), "P02": round(250 * 2.1 / 5.6, 2), "P03": round(250 * 2 / 5.6, 2)}
    assert abs(sum(u.values()) - 250) < 0.05
    assert (fab.CONTRATOS / "C1" / "rateios" / "semanal-2026-11-02.md").exists()


def test_rateio_senior_da_area_e_sem_participacao(fab, tmp_path):
    _equipe(fab, tmp_path)
    (fab.CONTRATOS / "C1" / "RATEIO.yaml").write_text("modo: senior_da_area\n")
    _participacoes(fab, ["2026-11-03,P01,OS1,M1,REVISAO,revisou,PR 1,", "2026-11-04,P02,OS1,M1,CONDUCAO,fez,commit abc,",
                         "2026-11-05,P03,OS1,M2,CORRECAO,corrigiu,ata 3,"])
    (fab.CONTRATOS / "C1" / "RATEIO_TOTAIS.csv").write_text("periodo,data_inicio,total_ust,base,documento\nsemanal,2026-11-02,250,aceito,e-mail fiscal\n")
    r = fab.rateio("C1", "semanal", "2026-11-06")
    u = {l["profissional_id"]: l["ust"] for l in r["linhas"]}
    assert u["P02"] == 0 and u["P01"] > 0 and u["P03"] > 0 and abs(sum(u.values()) - 250) < 0.05
    assert next(l for l in r["linhas"] if l["profissional_id"] == "P01")["responsavel_area"]
    vazio = fab.rateio("C1", "semanal", "2026-12-01", total=100)
    assert vazio["linhas"] == [] and vazio["nao_atribuido"] == 100


def test_planilha_gerar_e_importar(fab, tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    x = fab.gerar_planilha(tmp_path / "p.xlsx")
    wb = openpyxl.load_workbook(x)
    assert {"LEIA-ME", "CONTRATO", "PROFISSIONAIS", "PARTICIPACOES", "RATEIO_TOTAIS", "PROJETOS"} <= set(wb.sheetnames)
    wb["PROFISSIONAIS"].append(["Ana Sênior", "Dev", CPF_OK, "BACKEND", "SENIOR"])
    wb["RATEIO_TOTAIS"].append(["semanal", "2026-11-02", "250", "aceito", "e-mail"])
    for row in wb["CONTRATO"].iter_rows(min_row=2):
        if row[0].value == "contratante.orgao":
            row[1].value = "Prefeitura Exemplo"
    wb.save(x)
    r = fab.importar_planilha("C9", x)
    assert r["profissionais"]["novos"] == 1 and r["rateio_totais"] == 1 and r["contrato_campos"] == 1
    assert yaml.safe_load((fab.CONTRATOS / "C9/contrato.yaml").read_text())["contratante"]["orgao"] == "Prefeitura Exemplo"
    assert "#" not in (fab.CONTRATOS / "C9/RATEIO_TOTAIS.csv").read_text()  # linha de exemplo ignorada


def test_novo_repositorio_com_stack(fab, tmp_path):
    destino = fab.novo_repositorio(tmp_path / "pmx-001-sgd", "PMX-001-SGD", "Gestão Documental", "Prefeitura X", "CT-1",
                                   ["backend=python-fastapi", "frontend=react-vite"])
    pj = yaml.safe_load((destino / "PROJETO.yaml").read_text())
    assert [c["stack"] for c in pj["componentes"]] == ["python-fastapi", "react-vite"]
    assert (destino / "projetos/gestao-documental/backend/app/main.py").read_text().count("Gestão Documental") == 3
    for f in ("AGENTS.md", "CLAUDE.md", ".github/workflows/ci.yml", ".gitignore", "contratos/CT-1/contrato.yaml",
              ".claude/agents/g01-diretor-geral.md", "fabrica/VERSAO_MODELO", ".git"):
        assert (destino / f).exists(), f
    assert json.loads((destino / "fabrica/comunicacao/AGENT_TASKS.json").read_text())["tarefas"] == []
    with pytest.raises(fab.ErroFabrica):
        fab.novo_repositorio(tmp_path / "x", "ID", "S", componentes=["backend=cobol"])


# ---------------------------------------------- edital, documento base, saldo, fechamento, PPJ

def test_numero_formato_brasileiro(fab):
    assert fab.numero("1.500 UST") == 1500 and fab.numero("10,5") == 10.5 and fab.numero("10 UST fictícias") == 10
    assert fab.numero("") is None


def test_cadastro_so_com_nome_e_funcao(fab):
    fab.novo_contrato("C1")
    pid = fab.adicionar_profissional("C1", "João da Silva", "Analista de Requisitos")
    assert pid == "P01" and fab.carregar_profissionais("C1")[0]["funcao"] == "Analista de Requisitos"
    assert fab.adicionar_profissional("C1", "João da Silva", "Analista de Requisitos") == "P01"  # não duplica


def _edital(fab, extra=""):
    (fab.CONTRATOS / "C1" / "EDITAL.yaml").write_text(
        "documentos:\n  ppj: {titulo: 'Plano de Trabalho', secoes_extras: [{nome: 'Plano de Transição', orientacao: 'TR 8.2'}]}\n"
        "  fechamento: {titulo: 'Boletim Diário'}\n"
        "equipe_exigida:\n"
        "  - {perfil: 'Gerente de Projeto', quantidade: 1, palavras_chave: [gerente], certificacoes: [PMP], experiencia_anos: 5, origem: 'TR 7.1'}\n"
        "  - {perfil: 'Desenvolvedor', quantidade: 2, palavras_chave: [desenvolvedor], origem: 'TR 7.2'}\n"
        "tecnologias_exigidas: [{nome: PostgreSQL, origem: 'TR 4'}, {nome: COBOL, origem: 'TR 4'}]\n"
        "certificacoes_empresa_exigidas: [{nome: 'ISO 27001'}]\n" + extra)


def test_confronto_edital_com_documento_base(fab):
    fab.novo_contrato("C1")
    arq = fab.CONTRATOS / "C1" / "eq.csv"
    arq.write_text("nome,funcao,anos_experiencia,certificacoes\nAna,Gerente de Projeto,3,PMP\nBeto,Desenvolvedor Backend,,\n")
    fab.importar_profissionais("C1", arq)
    (fab.CONTRATOS / "C1" / "BASE.yaml").write_text(
        "empresa: {razao_social: X Ltda, cnpj: '00', responsavel_legal: Y, preposto: Z}\n"
        "capacidades: [{tipo: CERTIFICACAO_EMPRESA, item: ISO 27001, evidencia: cert.pdf}]\n")
    _edital(fab)
    r = fab.confrontar_edital("C1")
    txt = " | ".join(r["atende"] + r["ajustar"] + r["falta"])
    assert any("Gerente de Projeto: Ana tem a função, mas falta: experiência" in x for x in r["ajustar"])
    assert any("Desenvolvedor: Beto (1 de 2)" in x for x in r["atende"]) and any("Desenvolvedor: faltam 1" in x for x in r["falta"])
    assert any("PostgreSQL" in x for x in r["atende"]) and any("COBOL" in x for x in r["falta"])
    assert any("ISO 27001" in x for x in r["atende"]) and "razao social" not in txt
    assert (fab.CONTRATOS / "C1" / "CONFRONTO_EDITAL.md").exists()


def test_ppj_e_fechamento_adaptados_ao_edital(fab, tmp_path):
    _equipe(fab, tmp_path)
    _edital(fab)
    c = yaml.safe_load((fab.CONTRATOS / "C1/contrato.yaml").read_text())
    c["medicao"]["quantidade_contratada"] = "1.000 UST"
    (fab.CONTRATOS / "C1/contrato.yaml").write_text(yaml.safe_dump(c, allow_unicode=True))
    (fab.CONTRATOS / "C1/medicoes").mkdir(exist_ok=True)
    (fab.CONTRATOS / "C1/medicoes/OS1.json").write_text(json.dumps(
        {"contrato": "C1", "os": "OS1", "medido_em": "x", "totais": {"previsto": 300, "comprovado": 200, "aceito": 120}}))
    _participacoes(fab, ["2026-11-03,P01,OS1,M1,REVISAO,revisou,PR 1,", "2026-11-03,P02,OS1,M1,CONDUCAO,fez,commit abc,"])
    (fab.CONTRATOS / "C1/RATEIO_TOTAIS.csv").write_text("periodo,data_inicio,total_ust,base,documento\ndiario,2026-11-03,40,comprovado,registro do gestor\n")
    s = fab.saldo("C1")
    assert (s["contratado"], s["saldo_oficial"], s["saldo_projetado"]) == (1000, 880, 800)
    md = fab.fechamento("C1", "2026-11-03").read_text()
    assert md.startswith("# Boletim Diário — 2026-11-03") and "Ana Sênior" in md and "Beto Júnior" in md
    assert "40 UST" in md and "| 1000 UST |" in md
    assert fab.saldo("C1")["dias_para_esgotar"] == 22  # 880 / 40
    p = fab.ppj("C1").read_text()
    assert p.startswith("# Plano de Trabalho — C1") and "Plano de Transição (exigida pelo edital)" in p and "Ana Sênior" in p


def test_documento_base_importa_empresa_e_capacidades(fab, tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    x = fab.gerar_planilha(tmp_path / "base.xlsx")
    wb = openpyxl.load_workbook(x)
    for row in wb["EMPRESA"].iter_rows(min_row=2):
        if row[0].value == "razao_social":
            row[1].value = "Empresa Exemplo Ltda"
    wb["CAPACIDADES"].append(["TECNOLOGIA", "Java / Spring Boot", "5 sistemas", "atestado 1"])
    wb["PROFISSIONAIS"].append(["Ana", "Gerente de Projeto"])
    wb.save(x)
    r = fab.importar_planilha("C5", x)
    base = yaml.safe_load((fab.CONTRATOS / "C5/BASE.yaml").read_text())
    assert base["empresa"]["razao_social"] == "Empresa Exemplo Ltda" and base["capacidades"][0]["item"] == "Java / Spring Boot"
    assert r["profissionais"]["novos"] == 1


# ----------------------------------------------------------------------------- Word

def _tem_word():
    r = subprocess.run(["node", "-e", "require('docx')"], capture_output=True)
    return r.returncode == 0


@pytest.mark.skipif(not _tem_word(), reason="Node.js com a biblioteca docx não disponível")
def test_word_relatorio_e_equipe_simplificada(fab, tmp_path, monkeypatch):
    monkeypatch.setenv("FABRICA_WORD", "1")
    fab.novo_contrato("C1")
    # 1) modelo em branco Nome | CPF | Cargo
    modelo = fab.equipe_modelo(tmp_path / "modelo.docx")
    assert zipfile.ZipFile(modelo).read("word/document.xml").count(b"<w:tr") >= 26
    # 2) "preenchido" pelo usuário (gerado aqui com a mesma ferramenta) e importado de volta
    md = tmp_path / "preenchido.md"
    md.write_text(f"# Equipe\n\n| Nome | CPF | Cargo |\n|---|---|---|\n| Ana Souza | {CPF_OK} | Gerente de Projeto |\n| Beto Lima |  | Desenvolvedor |\n|  |  |  |\n")
    preenchido = fab.exportar_word(md, saida=tmp_path / "preenchido.docx", capa=False)
    r = fab.importar_profissionais("C1", preenchido)
    assert r["novos"] == 2 and not r["erros"]
    assert [p["funcao"] for p in fab.carregar_profissionais("C1")] == ["Gerente de Projeto", "Desenvolvedor"]
    # 3) documento oficial simplificado (privado, 600, com CPF formatado)
    of = fab.equipe_oficial("C1")
    assert of.suffix == ".docx" and "privado" in str(of) and oct(of.stat().st_mode)[-3:] == "600"
    xml = zipfile.ZipFile(of).read("word/document.xml").decode()
    assert "529.982.247-25" in xml and "Gerente de Projeto" in xml and "RESTRITO" in zipfile.ZipFile(of).read("word/footer1.xml").decode()
    # 4) relatório com capa e versão Word
    rel = fab.relatorio("C1", "mensal", "2026-11-01")
    assert rel.with_suffix(".docx").exists()
