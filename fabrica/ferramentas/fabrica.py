#!/usr/bin/env python3
"""CLI da Fábrica de Software Governamental.

Uso rápido (na raiz do repositório):
    python3 fabrica/ferramentas/fabrica.py iniciar
    python3 fabrica/ferramentas/fabrica.py --help

Princípio central: a CLI só registra o que pode ser comprovado. Commits vêm do
git, resultados de testes vêm de execuções reais (JUnit XML), participação
humana e aceite vêm de registros preenchidos por pessoas. Nada é inventado.
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yaml

TZ = ZoneInfo(os.environ.get("FABRICA_TZ", "America/Sao_Paulo"))
RAIZ = Path(os.environ.get("FABRICA_RAIZ", Path(__file__).resolve().parents[2]))
FAB = RAIZ / "fabrica"
COM = FAB / "comunicacao"
CONTRATOS = RAIZ / "contratos"

ESTADOS = ["BACKLOG", "READY", "IN_PROGRESS", "IN_REVIEW", "TESTING", "BLOCKED", "DONE"]
TRANSICOES = {
    "BACKLOG": {"READY", "BLOCKED"},
    "READY": {"IN_PROGRESS", "BLOCKED", "BACKLOG"},
    "IN_PROGRESS": {"IN_REVIEW", "BLOCKED", "READY"},
    "IN_REVIEW": {"TESTING", "IN_PROGRESS", "BLOCKED"},
    "TESTING": {"DONE", "IN_PROGRESS", "BLOCKED"},
    "BLOCKED": {"READY", "IN_PROGRESS", "BACKLOG"},
    "DONE": {"IN_PROGRESS"},  # reabertura exige nota
}
PRIORIDADES = ["BAIXA", "MEDIA", "ALTA", "CRITICA"]
TIPOS_PARTICIPACAO = ["CONDUCAO", "ORIENTACAO", "REVISAO", "CORRECAO", "APROVACAO"]

EVIDENCIAS_OBRIGATORIAS = [
    "ESCOPO.md", "REQUISITOS.md", "ARQUITETURA.md", "CODIGO_ALTERADO.md",
    "COMMITS.json", "TESTES.json", "LOGS_TESTES", "SEGURANCA.md", "PREVIEW.md",
    "SCREENSHOTS", "REVISOES.md", "RESPONSAVEIS.md", "MEDICAO.md",
    "IMPLANTACAO.md", "ACEITE.md",
]

PADROES_SEGREDO = [
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"sk-[A-Za-z0-9]{32,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
]


class ErroFabrica(Exception):
    """Erro de regra de negócio da fábrica (mensagem exibida ao usuário)."""


# --------------------------------------------------------------------------- util

def agora() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def hoje() -> str:
    return datetime.now(TZ).date().isoformat()


def ler_yaml(p: Path) -> Any:
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def gravar_json(p: Path, dados: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(p)


def ler_json(p: Path, padrao: Any = None) -> Any:
    if not p.exists():
        return padrao
    return json.loads(p.read_text(encoding="utf-8"))


def frontmatter(p: Path) -> dict:
    """Lê o bloco YAML entre '---' no topo de um arquivo Markdown."""
    if not p.exists():
        return {}
    texto = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}


def git(*args: str, cwd: Path = RAIZ) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise ErroFabrica(f"git {' '.join(args)} falhou: {r.stderr.strip()}")
    return r.stdout


def commit_existe(sha: str) -> bool:
    r = subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=RAIZ,
                       capture_output=True)
    return r.returncode == 0


def mascarar(texto: str) -> str:
    """Oculta senha em URLs de conexão (usuario:senha@host)."""
    return re.sub(r"://([^:/@]+):[^@]+@", r"://\1:***@", texto)


def rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(RAIZ))
    except ValueError:
        return str(p)


# ------------------------------------------------------------------ agentes

def carregar_registro() -> dict:
    return ler_yaml(FAB / "agentes" / "registry.yaml")


def gerar_agentes(destino: Path | None = None) -> list[Path]:
    reg = carregar_registro()
    destino = destino or (RAIZ / ".claude" / "agents")
    destino.mkdir(parents=True, exist_ok=True)
    perfis = reg["perfis_ferramentas"]
    nomes = {a["id"]: a["nome"] for a in reg["agentes"]}
    gerados = []
    for a in reg["agentes"]:
        ferramentas = ", ".join(perfis[a["perfil"]])
        desc = (f"{a['id']} — {a['nome']}. {a['funcao']} "
                f"Use quando a tarefa no quadro estiver atribuída a {a['id']}.")
        linhas = [
            "---",
            f"name: {a['slug']}",
            f"description: {json.dumps(desc, ensure_ascii=False)}",
            f"tools: {ferramentas}",
            "---",
            "",
            f"<!-- ARQUIVO GERADO por fabrica.py agentes gerar a partir de fabrica/agentes/registry.yaml. Edite o registro, não este arquivo. -->",
            "",
            f"# {a['id']} — {a['nome']}",
            "",
            f"**Equipe:** {'Fábrica Governamental' if a['equipe'] == 'governanca' else 'Engenharia de Software'}  ",
            f"**Função:** {a['funcao']}",
        ]
        if a.get("equivale"):
            linhas.append(f"**Equivale a:** {a['equivale']} — {nomes.get(a['equivale'], '')} (mesmo escopo; use um ou outro, não ambos na mesma tarefa)")
        linhas += ["", "## Responsabilidades", *[f"- {r}" for r in a["responsabilidades"]]]
        linhas += ["", "## Entradas", *[f"- {e}" for e in a["entradas"]]]
        linhas += ["", "## Saídas", *[f"- {s}" for s in a["saidas"]]]
        linhas += ["", "## Critério de conclusão", a["conclusao"]]
        linhas += ["", "## Comunica-se com",
                   *[f"- {c} — {nomes.get(c, '?')}" for c in a.get("comunica_com", [])]]
        linhas += ["", "## Como registrar o trabalho",
                   "```bash",
                   f"python3 fabrica/ferramentas/fabrica.py tarefas listar --agente {a['id']}",
                   f"python3 fabrica/ferramentas/fabrica.py tarefas mover <ID> IN_PROGRESS --por {a['id']}",
                   f"python3 fabrica/ferramentas/fabrica.py msg --de {a['id']} --para <AGENTE> --tarefa <ID> --texto \"...\"",
                   f"python3 fabrica/ferramentas/fabrica.py bloqueio --por {a['id']} --tarefa <ID> --texto \"...\"",
                   "```",
                   "", "## Regras obrigatórias", *[f"- {r}" for r in reg["regras_comuns"]], ""]
        p = destino / f"{a['slug']}.md"
        p.write_text("\n".join(linhas), encoding="utf-8")
        gerados.append(p)
    gerar_tabela_equipe(reg)
    return gerados


def gerar_tabela_equipe(reg: dict) -> Path:
    """Documento legível com a equipe de agentes (para o usuário e para o Codex)."""
    L = ["# Equipe de agentes da Fábrica", "",
         "Gerado por `fabrica.py agentes gerar` a partir de `fabrica/agentes/registry.yaml`.", ""]
    for equipe, titulo in (("governanca", "Fábrica Governamental (G01–G20)"), ("engenharia", "Engenharia de Software (E01–E20)")):
        L += [f"## {titulo}", "", "| ID | Agente | Função | Ferramentas | Equivale |", "|---|---|---|---|---|"]
        for a in reg["agentes"]:
            if a["equipe"] == equipe:
                L.append(f"| {a['id']} | {a['nome']} | {a['funcao']} | {a['perfil']} | {a.get('equivale', '')} |")
        L.append("")
    L += ["## Perfis de ferramentas (menor privilégio)", ""]
    L += [f"- **{k}**: {', '.join(v)}" for k, v in reg["perfis_ferramentas"].items()]
    p = FAB / "docs" / "EQUIPE_AGENTES.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    return p


def verificar_agentes() -> list[str]:
    reg = carregar_registro()
    problemas = []
    ids = [a["id"] for a in reg["agentes"]]
    if len(ids) != len(set(ids)):
        problemas.append("IDs de agentes duplicados no registro")
    for equipe in ("governanca", "engenharia"):
        n = sum(1 for a in reg["agentes"] if a["equipe"] == equipe)
        if n != 20:
            problemas.append(f"equipe {equipe} tem {n} agentes (esperado 20)")
    for a in reg["agentes"]:
        p = RAIZ / ".claude" / "agents" / f"{a['slug']}.md"
        if not p.exists():
            problemas.append(f"arquivo ausente: {rel(p)}")
            continue
        fm = frontmatter(p)
        if fm.get("name") != a["slug"] or not fm.get("description") or not fm.get("tools"):
            problemas.append(f"frontmatter inválido: {rel(p)}")
        for c in a.get("comunica_com", []):
            if c not in ids:
                problemas.append(f"{a['id']} comunica com agente inexistente {c}")
        if a["perfil"] not in reg["perfis_ferramentas"]:
            problemas.append(f"{a['id']} com perfil inexistente")
    return problemas


# ------------------------------------------------------------- comunicação

def arq_tarefas() -> Path:
    return COM / "AGENT_TASKS.json"


def carregar_tarefas() -> dict:
    return ler_json(arq_tarefas(), {"versao": 1, "tarefas": []})


def ids_agentes() -> set[str]:
    return {a["id"] for a in carregar_registro()["agentes"]}


def criar_tarefa(*, agente: str, descricao: str, prioridade: str = "MEDIA",
                 contrato: str = "", os_: str = "", modulo: str = "",
                 dependencias: list[str] | None = None, arquivos: list[str] | None = None,
                 prazo: str = "", profissional: str = "", por: str = "G14") -> dict:
    if agente not in ids_agentes():
        raise ErroFabrica(f"agente inexistente: {agente}")
    if prioridade not in PRIORIDADES:
        raise ErroFabrica(f"prioridade inválida: {prioridade} (use {PRIORIDADES})")
    if prazo:
        date.fromisoformat(prazo)
    q = carregar_tarefas()
    existentes = {t["id"] for t in q["tarefas"]}
    for d in dependencias or []:
        if d not in existentes:
            raise ErroFabrica(f"dependência inexistente: {d}")
    n = max([int(t["id"].split("-")[1]) for t in q["tarefas"]] or [0]) + 1
    t = {
        "id": f"T-{n:04d}", "contrato": contrato, "os": os_, "modulo": modulo,
        "agente": agente, "profissional": profissional, "descricao": descricao,
        "prioridade": prioridade, "dependencias": dependencias or [],
        "arquivos": arquivos or [], "prazo": prazo, "status": "BACKLOG",
        "resultado": "", "evidencias": [], "pendencias": [],
        "historico": [{"em": agora(), "de": None, "para": "BACKLOG", "por": por, "nota": "criada"}],
    }
    q["tarefas"].append(t)
    gravar_json(arq_tarefas(), q)
    return t


def _conflito_arquivos(q: dict, t: dict) -> list[str]:
    conflitos = []
    for o in q["tarefas"]:
        if o["id"] == t["id"] or o["status"] != "IN_PROGRESS":
            continue
        for a in t["arquivos"]:
            for b in o["arquivos"]:
                if a == b or fnmatch.fnmatch(a, b) or fnmatch.fnmatch(b, a) \
                        or a.startswith(b.rstrip("/") + "/") or b.startswith(a.rstrip("/") + "/"):
                    conflitos.append(f"{a} (reservado por {o['id']})")
    return conflitos


def mover_tarefa(tid: str, para: str, *, por: str, nota: str = "",
                 resultado: str = "", evidencias: list[str] | None = None) -> dict:
    if para not in ESTADOS:
        raise ErroFabrica(f"estado inválido: {para}")
    q = carregar_tarefas()
    t = next((x for x in q["tarefas"] if x["id"] == tid), None)
    if not t:
        raise ErroFabrica(f"tarefa inexistente: {tid}")
    de = t["status"]
    if para not in TRANSICOES[de]:
        raise ErroFabrica(f"transição não permitida: {de} -> {para}")
    if de == "DONE" and not nota:
        raise ErroFabrica("reabrir tarefa DONE exige --nota")
    if para == "IN_PROGRESS":
        estados = {x["id"]: x["status"] for x in q["tarefas"]}
        pend = [d for d in t["dependencias"] if estados.get(d) != "DONE"]
        if pend:
            raise ErroFabrica(f"dependências não concluídas: {', '.join(pend)}")
        conf = _conflito_arquivos(q, t)
        if conf:
            raise ErroFabrica("conflito de arquivos: " + "; ".join(conf))
    if para == "BLOCKED" and not nota:
        raise ErroFabrica("bloquear exige --nota com o motivo")
    if resultado:
        t["resultado"] = resultado
    if evidencias:
        t["evidencias"] = sorted(set(t["evidencias"]) | set(evidencias))
    if para == "DONE":
        if not t["resultado"] or not t["evidencias"]:
            raise ErroFabrica("DONE exige --resultado e ao menos uma --evidencia")
        faltando = [e for e in t["evidencias"] if not (RAIZ / e).exists() and not commit_existe(e)]
        if faltando:
            raise ErroFabrica("evidências não encontradas (nem arquivo nem commit): " + ", ".join(faltando))
    t["status"] = para
    t["historico"].append({"em": agora(), "de": de, "para": para, "por": por, "nota": nota})
    gravar_json(arq_tarefas(), q)
    return t


def validar_quadro() -> list[str]:
    q = carregar_tarefas()
    erros = []
    ids = {t["id"] for t in q["tarefas"]}
    agentes = ids_agentes()
    for t in q["tarefas"]:
        if t["status"] not in ESTADOS:
            erros.append(f"{t['id']}: estado inválido {t['status']}")
        if t["agente"] not in agentes:
            erros.append(f"{t['id']}: agente inexistente {t['agente']}")
        for d in t["dependencias"]:
            if d not in ids:
                erros.append(f"{t['id']}: dependência inexistente {d}")
        hist = t.get("historico", [])
        if not hist or hist[-1]["para"] != t["status"]:
            erros.append(f"{t['id']}: histórico inconsistente com o status")
        for h in hist[1:]:
            if h["para"] not in TRANSICOES.get(h["de"], set()):
                erros.append(f"{t['id']}: transição inválida no histórico {h['de']}->{h['para']}")
        if t["status"] == "IN_PROGRESS":
            for c in _conflito_arquivos(q, t):
                erros.append(f"{t['id']}: conflito {c}")
    return erros


def registrar_msg(de: str, para: str, texto: str, tarefa: str = "", tipo: str = "INFO") -> dict:
    ag = ids_agentes() | {"HUMANO", "TODOS"}
    if de not in ag or para not in ag:
        raise ErroFabrica("remetente/destinatário inválido")
    m = {"em": agora(), "de": de, "para": para, "tarefa": tarefa, "tipo": tipo, "texto": texto}
    COM.mkdir(parents=True, exist_ok=True)
    with open(COM / "AGENT_MESSAGES.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(m, ensure_ascii=False) + "\n")
    return m


def _anexar_md(nome: str, prefixo: str, titulo: str, corpo: str, por: str) -> str:
    p = COM / nome
    texto = p.read_text(encoding="utf-8") if p.exists() else ""
    n = len(re.findall(rf"^## {prefixo}-\d+", texto, re.M)) + 1
    ident = f"{prefixo}-{n:04d}"
    with open(p, "a", encoding="utf-8") as f:
        f.write(f"\n## {ident} — {titulo}\n\n- Data: {agora()}\n- Registrado por: {por}\n\n{corpo}\n")
    return ident


# ------------------------------------------------------------- contratos / OS

def dir_contrato(cid: str) -> Path:
    d = CONTRATOS / cid
    if not d.exists():
        raise ErroFabrica(f"contrato inexistente: {cid} (use: contrato novo {cid})")
    return d


def novo_contrato(cid: str) -> Path:
    d = CONTRATOS / cid
    if d.exists():
        raise ErroFabrica(f"contrato já existe: {cid}")
    tpl = FAB / "templates"
    (d / "documentos").mkdir(parents=True)
    for sub in ("os", "evidencias", "relatorios/diarios", "relatorios/mensais", "medicoes", "checklist"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    form = (tpl / "FORMULARIO_CONTRATO.yaml").read_text(encoding="utf-8")
    (d / "contrato.yaml").write_text(form.replace("<ID_CONTRATO>", cid), encoding="utf-8")
    for nome in ("PROFISSIONAIS.csv", "PARTICIPACOES.csv", "TABELA_UST.csv",
                 "MATRIZ_RASTREABILIDADE.md", "GEC_TEMPLATE.md"):
        destino = d / ("GEC.md" if nome == "GEC_TEMPLATE.md" else nome)
        shutil.copy(tpl / nome, destino)
    (d / "documentos" / "LEIA-ME.md").write_text(
        "Coloque aqui edital, TR, contrato, anexos, aditivos e OS (PDF/DOCX).\n", encoding="utf-8")
    return d


def _vazios(obj: Any, prefixo: str = "") -> list[str]:
    faltam = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.startswith("_"):
                continue
            faltam += _vazios(v, f"{prefixo}{k}.")
    elif isinstance(obj, list):
        if not obj:
            faltam.append(prefixo.rstrip("."))
        for i, v in enumerate(obj):
            faltam += _vazios(v, f"{prefixo}{i}.")
    elif obj in (None, "") or (isinstance(obj, str) and obj.startswith("<")):
        faltam.append(prefixo.rstrip("."))
    return faltam


def campos_faltantes(cid: str) -> list[str]:
    return _vazios(ler_yaml(dir_contrato(cid) / "contrato.yaml"))


def carregar_os(cid: str, osid: str) -> dict:
    p = dir_contrato(cid) / "os" / f"{osid}.yaml"
    if not p.exists():
        raise ErroFabrica(f"OS inexistente: {rel(p)}")
    o = ler_yaml(p)
    o["_dir_projeto"] = RAIZ / o["projeto"]
    return o


def exigir_autorizacao(o: dict) -> None:
    a = o.get("autorizacao") or {}
    if not (a.get("autorizado") is True and a.get("autorizado_por") and a.get("data")):
        raise ErroFabrica(f"{o['os']} sem autorização registrada (autorizado/autorizado_por/data). "
                          "Não executo OS sem autorização.")


def dir_mod(cid: str, osid: str, mid: str) -> Path:
    return CONTRATOS / cid / "evidencias" / osid / mid


def tabela_ust(cid: str) -> dict[str, dict]:
    p = dir_contrato(cid) / "TABELA_UST.csv"
    with open(p, encoding="utf-8") as f:
        return {r["codigo"]: r for r in csv.DictReader(f) if r.get("codigo")}


# ----------------------------------------------------------------- evidências

def preparar_evidencias(cid: str, osid: str) -> list[Path]:
    """Cria a pasta de cada módulo com modelos (sem sobrescrever o que existe)."""
    o = carregar_os(cid, osid)
    tpl = FAB / "templates" / "evidencias"
    criados = []
    for m in o["modulos"]:
        d = dir_mod(cid, osid, m["id"])
        (d / "LOGS_TESTES").mkdir(parents=True, exist_ok=True)
        (d / "SCREENSHOTS").mkdir(parents=True, exist_ok=True)
        for arq in sorted(tpl.glob("*.md")):
            alvo = d / arq.name
            if alvo.exists():
                continue
            txt = arq.read_text(encoding="utf-8")
            for k, v in {"<CONTRATO>": cid, "<OS>": osid, "<MODULO>": m["id"],
                         "<NOME_MODULO>": m["nome"], "<UST_PREVISTO>": str(m.get("ust_previsto", "")),
                         "<ITEM_TABELA>": m.get("item_tabela", "")}.items():
                txt = txt.replace(k, v)
            alvo.write_text(txt, encoding="utf-8")
            criados.append(alvo)
    return criados


def coletar_commits(cid: str, osid: str) -> dict[str, int]:
    """Lê o git (real) e grava COMMITS.json e CODIGO_ALTERADO.md por módulo."""
    o = carregar_os(cid, osid)
    proj = o["projeto"].rstrip("/")
    total = {}
    for m in o["modulos"]:
        d = dir_mod(cid, osid, m["id"])
        caminhos = [f"{proj}/{c}" for c in m.get("caminhos", [])]
        commits = []
        if caminhos:
            fmt = "%H%x1f%an%x1f%ae%x1f%aI%x1f%s"
            saida = git("log", f"--pretty=format:{fmt}", "--", *caminhos)
            for linha in filter(None, saida.splitlines()):
                sha, an, ae, data, assunto = linha.split("\x1f")
                arqs = [a for a in git("show", "--name-status", "--pretty=format:", sha, "--", *caminhos).splitlines() if a.strip()]
                commits.append({"sha": sha, "autor": an, "email_autor": ae, "data": data,
                                "mensagem": assunto, "arquivos": arqs})
        gravar_json(d / "COMMITS.json", {
            "fonte": "git log (gerado por fabrica.py evidencias commits)",
            "gerado_em": agora(), "caminhos": caminhos, "commits": commits})
        linhas = [f"# Código alterado — {m['id']} {m['nome']}", "",
                  "Gerado a partir do git. Cada linha é um arquivo realmente alterado.", "",
                  "| Commit | Data | Status | Arquivo |", "|---|---|---|---|"]
        for c in commits:
            for a in c["arquivos"]:
                st, _, caminho = a.partition("\t")
                linhas.append(f"| `{c['sha'][:10]}` | {c['data'][:10]} | {st} | `{caminho}` |")
        if not commits:
            linhas.append("| — | — | — | NENHUM COMMIT ENCONTRADO |")
        atuais = []
        for c in caminhos:
            atuais += [a for a in git("ls-files", "--", c).splitlines() if a]
        linhas += ["", f"## Arquivos atuais do módulo ({len(atuais)})", "", *[f"- `{a}`" for a in sorted(set(atuais))], ""]
        (d / "CODIGO_ALTERADO.md").write_text("\n".join(linhas), encoding="utf-8")
        total[m["id"]] = len(commits)
    return total


def ler_junit(p: Path) -> dict:
    raiz = ET.parse(p).getroot()
    suites = [raiz] if raiz.tag == "testsuite" else list(raiz.iter("testsuite"))
    r = {"testes": 0, "falhas": 0, "erros": 0, "ignorados": 0, "casos": []}
    vistos = set()
    for s in suites:
        for c in s.iter("testcase"):
            chave = (c.get("classname"), c.get("name"))
            if chave in vistos:
                continue
            vistos.add(chave)
            st = "PASSOU"
            if c.find("failure") is not None:
                st = "FALHOU"; r["falhas"] += 1
            elif c.find("error") is not None:
                st = "ERRO"; r["erros"] += 1
            elif c.find("skipped") is not None:
                st = "IGNORADO"; r["ignorados"] += 1
            r["testes"] += 1
            r["casos"].append({"suite": c.get("classname") or s.get("name"), "nome": c.get("name"),
                               "tempo_s": float(c.get("time") or 0), "status": st})
    return r


def executar_testes(cid: str, osid: str, somente: str | None = None) -> dict[str, dict]:
    """Executa de fato os comandos de teste de cada módulo e grava resultados reais."""
    o = carregar_os(cid, osid)
    exigir_autorizacao(o)
    resultados = {}
    for m in o["modulos"]:
        if somente and m["id"] != somente:
            continue
        d = dir_mod(cid, osid, m["id"])
        (d / "LOGS_TESTES").mkdir(parents=True, exist_ok=True)
        execucoes = []
        for t in m.get("testes", []):
            carimbo = datetime.now(TZ).strftime("%Y%m%dT%H%M%S")
            junit = d / "LOGS_TESTES" / f"{t['nome']}-{carimbo}.xml"
            log = d / "LOGS_TESTES" / f"{t['nome']}-{carimbo}.log"
            cmd = [c.replace("{junit}", str(junit)) for c in t["cmd"]]
            cwd = o["_dir_projeto"] / t.get("cwd", ".")
            ini = datetime.now(TZ)
            env = {**os.environ, **{k: str(v) for k, v in (t.get("env") or {}).items()}}
            r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
            fim = datetime.now(TZ)
            amb = "".join(f"# {k}={mascarar(env[k])}\n" for k in ("TEST_DATABASE_URL",) if env.get(k))
            log.write_text(f"$ (cd {rel(cwd)} && {' '.join(cmd)})\n# início: {ini.isoformat()}\n"
                           f"# fim: {fim.isoformat()}\n# código de saída: {r.returncode}\n{amb}\n"
                           f"{r.stdout}\n{r.stderr}", encoding="utf-8")
            if t.get("tipo") == "comando":  # verificação sem JUnit: vale o código de saída
                st = "PASSOU" if r.returncode == 0 else "FALHOU"
                res = {"testes": 1, "falhas": int(r.returncode != 0), "erros": 0, "ignorados": 0,
                       "casos": [{"suite": t["nome"], "nome": " ".join(cmd), "tempo_s": (fim - ini).total_seconds(), "status": st}]}
                junit = log
            else:
                res = ler_junit(junit) if junit.exists() else {"testes": 0, "falhas": 0, "erros": 1, "ignorados": 0, "casos": []}
            execucoes.append({"nome": t["nome"], "comando": " ".join(cmd), "cwd": rel(cwd),
                              "inicio": ini.isoformat(timespec="seconds"),
                              "fim": fim.isoformat(timespec="seconds"),
                              "codigo_saida": r.returncode, "junit": rel(junit), "log": rel(log), **res})
        total = {k: sum(e[k] for e in execucoes) for k in ("testes", "falhas", "erros", "ignorados")}
        dados = {"fonte": "execução real via fabrica.py testes executar", "modulo": m["id"],
                 "executado_em": agora(), "resumo": total,
                 "situacao": "APROVADO" if execucoes and total["testes"] > 0 and total["falhas"] == 0 and total["erros"] == 0 and all(e["codigo_saida"] == 0 for e in execucoes) else "REPROVADO",
                 "execucoes": execucoes}
        gravar_json(d / "TESTES.json", dados)
        resultados[m["id"]] = dados
    return resultados


# ------------------------------------------------------------------ auditoria

def auditar_modulo(cid: str, osid: str, m: dict) -> dict:
    d = dir_mod(cid, osid, m["id"])
    achados = []
    for e in EVIDENCIAS_OBRIGATORIAS:
        if e == "MEDICAO.md":  # é produzido pela medição (que depende desta auditoria); cobrado no checklist C081-C086
            continue
        if not (d / e).exists():
            achados.append({"severidade": "BLOQUEANTE", "item": e, "texto": "evidência obrigatória ausente"})
    commits = (ler_json(d / "COMMITS.json", {}) or {}).get("commits", [])
    if not commits:
        achados.append({"severidade": "BLOQUEANTE", "item": "COMMITS.json", "texto": "nenhum commit vinculado"})
    for c in commits:
        if not commit_existe(c["sha"]):
            achados.append({"severidade": "BLOQUEANTE", "item": "COMMITS.json", "texto": f"commit inexistente no git: {c['sha']}"})
    testes = ler_json(d / "TESTES.json", {}) or {}
    if testes.get("situacao") != "APROVADO":
        achados.append({"severidade": "BLOQUEANTE", "item": "TESTES.json", "texto": f"testes não aprovados ({testes.get('situacao', 'ausente')})"})
    for e in testes.get("execucoes", []):
        for k in ("junit", "log"):
            if not (RAIZ / e[k]).exists():
                achados.append({"severidade": "BLOQUEANTE", "item": k, "texto": f"arquivo citado não existe: {e[k]}"})
    caps = [p for p in (d / "SCREENSHOTS").glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")] if (d / "SCREENSHOTS").exists() else []
    if m.get("tem_interface") and not caps:
        achados.append({"severidade": "ALERTA", "item": "SCREENSHOTS", "texto": "módulo com interface sem captura real"})
    resp = frontmatter(d / "RESPONSAVEIS.md")
    if not resp.get("responsavel_tecnico") or str(resp.get("responsavel_tecnico")).upper().startswith("A CADASTRAR"):
        achados.append({"severidade": "PENDENCIA_HUMANA", "item": "RESPONSAVEIS.md", "texto": "profissional humano responsável não cadastrado"})
    rev = frontmatter(d / "REVISOES.md")
    if not rev.get("revisao_humana"):
        achados.append({"severidade": "PENDENCIA_HUMANA", "item": "REVISOES.md", "texto": "revisão humana não registrada"})
    for p in ("ESCOPO.md", "REQUISITOS.md", "ARQUITETURA.md", "SEGURANCA.md", "PREVIEW.md", "IMPLANTACAO.md"):
        if (d / p).exists() and "<PREENCHER>" in (d / p).read_text(encoding="utf-8"):
            achados.append({"severidade": "BLOQUEANTE", "item": p, "texto": "modelo não preenchido (<PREENCHER>)"})
    bloq = any(a["severidade"] == "BLOQUEANTE" for a in achados)
    return {"modulo": m["id"], "nome": m["nome"],
            "tecnico": "REPROVADO" if bloq else "APROVADO",
            "pendencias_humanas": [a for a in achados if a["severidade"] == "PENDENCIA_HUMANA"],
            "achados": achados, "commits": len(commits),
            "testes": testes.get("resumo", {}), "capturas": len(caps)}


def auditar(cid: str, osid: str) -> dict:
    o = carregar_os(cid, osid)
    mods = [auditar_modulo(cid, osid, m) for m in o["modulos"]]
    r = {"contrato": cid, "os": osid, "auditado_em": agora(), "agente": "G17", "modulos": mods}
    d = CONTRATOS / cid / "evidencias" / osid
    gravar_json(d / "AUDITORIA.json", r)
    linhas = [f"# Parecer de auditoria de evidências — {osid}", "",
              f"Gerado em {r['auditado_em']} pelo Auditor de Evidências (G17) via `fabrica.py auditar`.", "",
              "| Módulo | Técnico | Commits | Testes (ok/total) | Capturas | Pendências humanas |",
              "|---|---|---|---|---|---|"]
    for m in mods:
        t = m["testes"]
        ok = t.get("testes", 0) - t.get("falhas", 0) - t.get("erros", 0) - t.get("ignorados", 0)
        linhas.append(f"| {m['modulo']} {m['nome']} | {m['tecnico']} | {m['commits']} | {ok}/{t.get('testes', 0)} | {m['capturas']} | {len(m['pendencias_humanas'])} |")
    linhas += ["", "## Achados", ""]
    for m in mods:
        for a in m["achados"]:
            linhas.append(f"- **{m['modulo']}** [{a['severidade']}] {a['item']}: {a['texto']}")
    linhas += ["", "> APROVADO técnico significa que as evidências automáticas conferem. Não substitui revisão humana nem aceite do contratante.", ""]
    (d / "AUDITORIA.md").write_text("\n".join(linhas), encoding="utf-8")
    return r


# -------------------------------------------------------------------- medição

def medir(cid: str, osid: str) -> dict:
    """Memória de cálculo: previsto (OS), comprovado (auditoria técnica), aceito (registro humano)."""
    o = carregar_os(cid, osid)
    tab = tabela_ust(cid)
    aud = {m["modulo"]: m for m in auditar(cid, osid)["modulos"]}
    itens = []
    for m in o["modulos"]:
        cod = m.get("item_tabela", "")
        if cod not in tab:
            raise ErroFabrica(f"{m['id']}: item {cod!r} não existe na TABELA_UST.csv")
        item = tab[cod]
        prev = float(m.get("ust_previsto") or 0)
        a = aud[m["id"]]
        comprovado = prev if a["tecnico"] == "APROVADO" else 0.0
        ace = frontmatter(dir_mod(cid, osid, m["id"]) / "ACEITE.md")
        aceito = 0.0
        if str(ace.get("status", "")).upper() == "ACEITO" and ace.get("aceito_por") and ace.get("documento"):
            aceito = min(float(ace.get("quantidade_aceita") or 0), comprovado)
        memoria = (f"previsto={prev:g} {item['unidade']} (OS {osid}, item {cod}); "
                   f"comprovado={comprovado:g} pois auditoria técnica={a['tecnico']}"
                   f"{' (regra: integral somente com evidências completas)' if comprovado == 0 else ''}; "
                   f"aceito={aceito:g} ({'termo: ' + str(ace.get('documento')) if aceito else 'sem aceite registrado'})")
        itens.append({"modulo": m["id"], "nome": m["nome"], "item": cod,
                      "descricao_item": item["descricao"], "unidade": item["unidade"],
                      "referencia_contratual": item.get("referencia_contratual", ""),
                      "previsto": prev, "comprovado": comprovado, "aceito": aceito,
                      "evidencias": rel(dir_mod(cid, osid, m["id"])), "memoria": memoria,
                      "responsavel": frontmatter(dir_mod(cid, osid, m["id"]) / "RESPONSAVEIS.md").get("responsavel_tecnico", "")})
    tot = {k: sum(i[k] for i in itens) for k in ("previsto", "comprovado", "aceito")}
    r = {"contrato": cid, "os": osid, "medido_em": agora(), "agente": "G15",
         "aviso": o.get("aviso_medicao", ""), "itens": itens, "totais": tot}
    gravar_json(CONTRATOS / cid / "medicoes" / f"{osid}.json", r)
    linhas = [f"# Memória de cálculo — {osid}", "", f"Gerado em {r['medido_em']} pelo Medidor de UST (G15).", ""]
    if r["aviso"]:
        linhas += [f"> **{r['aviso']}**", ""]
    linhas += ["| Módulo | Item | Unid. | Previsto | Comprovado | Aceito | Responsável |", "|---|---|---|---|---|---|---|"]
    for i in itens:
        linhas.append(f"| {i['modulo']} {i['nome']} | {i['item']} | {i['unidade']} | {i['previsto']:g} | {i['comprovado']:g} | {i['aceito']:g} | {i['responsavel'] or '—'} |")
    linhas.append(f"| **Total** | | | **{tot['previsto']:g}** | **{tot['comprovado']:g}** | **{tot['aceito']:g}** | |")
    linhas += ["", "## Memória por item", "", *[f"- **{i['modulo']}**: {i['memoria']}" for i in itens],
               "", "## Regras aplicadas", "",
               "- Previsto: quantidade da OS para o item da tabela contratual.",
               "- Comprovado: igual ao previsto somente se a auditoria técnica do módulo for APROVADO (evidências completas, commits reais, testes reais sem falhas); caso contrário 0. Ajuste esta regra se o contrato prever medição parcial.",
               "- Aceito: somente com ACEITE.md em status ACEITO, com `aceito_por` e `documento` (termo do contratante). Nunca maior que o comprovado.",
               "- Não há conversão entre UST, pontos de função e horas.", ""]
    (CONTRATOS / cid / "medicoes" / f"{osid}.md").write_text("\n".join(linhas), encoding="utf-8")
    for i in itens:
        p = dir_mod(cid, osid, i["modulo"]) / "MEDICAO.md"
        p.write_text("\n".join([f"# Medição — {i['modulo']} {i['nome']}", "",
                                f"- Item contratual: {i['item']} — {i['descricao_item']} ({i['unidade']})",
                                f"- Referência contratual: {i['referencia_contratual'] or 'a confirmar'}",
                                f"- Previsto: {i['previsto']:g}", f"- Comprovado: {i['comprovado']:g}",
                                f"- Aceito: {i['aceito']:g}", "", f"Memória: {i['memoria']}", "",
                                f"Consolidado: `contratos/{cid}/medicoes/{osid}.md`", ""]), encoding="utf-8")
    return r


# ------------------------------------------------------------------ checklist

def checklist(cid: str, osid: str) -> dict:
    o = carregar_os(cid, osid)
    proj = o["_dir_projeto"]
    cdir = CONTRATOS / cid
    ck = ler_yaml(FAB / "qualidade" / "checklist_100.yaml")
    manuais = (ler_yaml(cdir / "checklist" / "resultados_humanos.yaml") or {}) if (cdir / "checklist" / "resultados_humanos.yaml").exists() else {}
    mods = [dir_mod(cid, osid, m["id"]) for m in o["modulos"]]
    med = ler_json(cdir / "medicoes" / f"{osid}.json")
    resultados = []

    def ultimo_junit(nome: str) -> tuple[str, str]:
        arqs = []  # execução mais recente de cada módulo
        if nome == "fabrica":
            arqs = sorted((cdir / "checklist").glob("fabrica-*.xml"))[-1:]
        else:
            for d in mods:
                ult = sorted((d / "LOGS_TESTES").glob(f"{nome}-*.xml"))
                arqs += ult[-1:]
        if not arqs:
            return "NAO_VERIFICADO", "nenhuma execução encontrada"
        piores = [ler_junit(a) for a in arqs]
        falhas = sum(p["falhas"] + p["erros"] for p in piores)
        total = sum(p["testes"] for p in piores)
        return ("APROVADO" if falhas == 0 and total > 0 else "REPROVADO"), f"{total} testes, {falhas} falhas ({rel(arqs[-1])})"

    for g in ck["grupos"]:
        for c in g["controles"]:
            res, evid = "NAO_VERIFICADO", "requer verificação humana"
            a = c.get("auto")
            if a:
                if "arquivo" in a:
                    p = (proj / a["arquivo"]) if not a["arquivo"].endswith((".yaml", "RASTREABILIDADE.md", "GEC.md")) else (cdir / a["arquivo"])
                    ok = p.exists()
                    res, evid = ("APROVADO" if ok else "REPROVADO"), rel(p)
                elif "evidencia" in a:
                    faltam = [rel(d) for d in mods if not (d / a["evidencia"]).exists()]
                    res = "APROVADO" if not faltam else "REPROVADO"
                    evid = f"{a['evidencia']} em {len(mods) - len(faltam)}/{len(mods)} módulos"
                elif "testes" in a:
                    res, evid = ultimo_junit(a["testes"])
                elif "sem_segredos" in a:
                    achados = varrer_segredos(proj)
                    res, evid = ("APROVADO" if not achados else "REPROVADO"), (", ".join(achados[:5]) or "nenhum padrão encontrado")
                elif "commits" in a:
                    ruins = []
                    for d in mods:
                        cs = (ler_json(d / "COMMITS.json", {}) or {}).get("commits", [])
                        if not cs or not all(commit_existe(x["sha"]) for x in cs):
                            ruins.append(d.name)
                    res, evid = ("APROVADO" if not ruins else "REPROVADO"), (f"sem commits válidos: {ruins}" if ruins else "todos os módulos com commits reais")
                elif "caso" in a:
                    tj = ler_json(dir_mod(cid, osid, a["caso"]["modulo"]) / "TESTES.json") or {}
                    casos = [c for e in tj.get("execucoes", []) for c in e["casos"] if a["caso"]["contem"] in c["nome"]]
                    if not casos:
                        res, evid = "NAO_VERIFICADO", f"caso '{a['caso']['contem']}' não executado"
                    else:
                        res = "APROVADO" if all(c["status"] == "PASSOU" for c in casos) else "REPROVADO"
                        evid = f"{a['caso']['modulo']}/TESTES.json: {len(casos)} caso(s) '{a['caso']['contem']}' ({tj.get('executado_em', '')[:16]})"
                elif "auditoria" in a:
                    au = ler_json(cdir / "evidencias" / osid / "AUDITORIA.json")
                    if not au:
                        res, evid = "NAO_VERIFICADO", "auditoria não executada"
                    else:
                        res = "APROVADO" if all(m["tecnico"] == "APROVADO" for m in au["modulos"]) else "REPROVADO"
                        evid = f"evidencias/{osid}/AUDITORIA.md ({au['auditado_em'][:16]})"
                elif "medicao" in a:
                    if not med:
                        res, evid = "REPROVADO", "medição não gerada"
                    else:
                        inval = [i["modulo"] for i in med["itens"] if i["comprovado"] > 0 and not Path(RAIZ / i["evidencias"]).exists()]
                        res = "APROVADO" if not inval else "REPROVADO"
                        evid = f"contratos/{cid}/medicoes/{osid}.json"
            if c["id"] in manuais:
                h = manuais[c["id"]]
                if h.get("resultado") and h.get("responsavel") and h.get("evidencia"):
                    res, evid = h["resultado"], f"{h['evidencia']} (por {h['responsavel']} em {h.get('data', '')})"
            resultados.append({"id": c["id"], "grupo": g["nome"], "descricao": c["descricao"],
                               "metodo": c["metodo"], "critico": c.get("critico", False),
                               "resultado": res, "evidencia": evid,
                               "responsavel": (manuais.get(c["id"]) or {}).get("responsavel", "G17 (automático)" if a else ""),
                               "data": hoje()})
    crit_rep = [r["id"] for r in resultados if r["critico"] and r["resultado"] == "REPROVADO"]
    crit_nv = [r["id"] for r in resultados if r["critico"] and r["resultado"] == "NAO_VERIFICADO"]
    situacao = "BLOQUEADA" if crit_rep else ("PENDENTE_VERIFICACAO_HUMANA" if crit_nv else "LIBERADA_PARA_HOMOLOGACAO")
    cont = {k: sum(1 for r in resultados if r["resultado"] == k) for k in ("APROVADO", "REPROVADO", "NAO_APLICAVEL", "NAO_VERIFICADO")}
    out = {"contrato": cid, "os": osid, "gerado_em": agora(), "situacao_entrega": situacao,
           "criticos_reprovados": crit_rep, "criticos_nao_verificados": crit_nv,
           "contagem": cont, "controles": resultados}
    gravar_json(cdir / "checklist" / f"{osid}.json", out)
    linhas = [f"# Checklist de 100 controles — {osid}", "", f"Gerado em {out['gerado_em']}.", "",
              f"**Situação da entrega: {situacao}**", "",
              f"Aprovados {cont['APROVADO']} · Reprovados {cont['REPROVADO']} · Não aplicáveis {cont['NAO_APLICAVEL']} · Não verificados {cont['NAO_VERIFICADO']}", ""]
    if crit_rep:
        linhas.append(f"Críticos reprovados (bloqueiam): {', '.join(crit_rep)}\n")
    if crit_nv:
        linhas.append(f"Críticos aguardando verificação humana: {', '.join(crit_nv)}\n")
    grupo = None
    for r in resultados:
        if r["grupo"] != grupo:
            grupo = r["grupo"]
            linhas += ["", f"## {grupo}", "", "| ID | Controle | Crítico | Resultado | Evidência | Responsável |", "|---|---|---|---|---|---|"]
        linhas.append(f"| {r['id']} | {r['descricao']} | {'sim' if r['critico'] else ''} | {r['resultado']} | {r['evidencia']} | {r['responsavel']} |")
    linhas += ["", "Para registrar verificação humana: edite `checklist/resultados_humanos.yaml` (resultado, responsavel, evidencia, data) e rode o checklist de novo.", ""]
    (cdir / "checklist" / f"{osid}.md").write_text("\n".join(linhas), encoding="utf-8")
    return out


def varrer_segredos(base: Path) -> list[str]:
    """Procura segredos nos arquivos VERSIONADOS (git ls-files) sob a pasta."""
    achados = []
    for nome in git("ls-files", "--", rel(base)).splitlines():
        p = RAIZ / nome
        if p.name == ".env" or p.name.endswith(".env") and not p.name.endswith(".example"):
            achados.append(f"{nome} (arquivo .env versionado)")
            continue
        if p.suffix.lower() in (".png", ".jpg", ".pdf", ".zip", ".ico", ".woff", ".woff2") or not p.is_file():
            continue
        try:
            texto = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if any(pad.search(texto) for pad in PADROES_SEGREDO):
            achados.append(nome)
    return achados


# ---------------------------------------------------------------- profissionais

def carregar_profissionais(cid: str) -> list[dict]:
    p = dir_contrato(cid) / "PROFISSIONAIS.csv"
    with open(p, encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("id") and not r["id"].startswith("#")]


def carregar_participacoes(cid: str) -> tuple[list[dict], list[str]]:
    p = dir_contrato(cid) / "PARTICIPACOES.csv"
    profs = {x["id"] for x in carregar_profissionais(cid)}
    validas, erros = [], []
    with open(p, encoding="utf-8") as f:
        for n, r in enumerate(csv.DictReader(f), start=2):
            if not r.get("data") or r["data"].startswith("#"):
                continue
            if r["profissional_id"] not in profs:
                erros.append(f"linha {n}: profissional {r['profissional_id']} não cadastrado")
            elif r["tipo"] not in TIPOS_PARTICIPACAO:
                erros.append(f"linha {n}: tipo {r['tipo']} inválido (use {TIPOS_PARTICIPACAO})")
            elif not r.get("evidencia"):
                erros.append(f"linha {n}: participação sem evidência")
            else:
                validas.append(r)
    return validas, erros


def estatisticas_producao(arquivo: Path) -> dict:
    """Média de UST ACEITA por profissional e complexidade, a partir de dados do contratado."""
    grupos: dict[tuple[str, str], list[float]] = {}
    with open(arquivo, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not r.get("profissional") or r["profissional"].startswith("#"):
                continue
            grupos.setdefault((r["profissional"], r.get("complexidade", "").upper()), []).append(float(r["ust_aceita"] or 0))
    saida = []
    for (prof, cx), vals in sorted(grupos.items()):
        saida.append({"profissional": prof, "complexidade": cx, "os_registradas": len(vals),
                      "ust_aceita_total": round(sum(vals), 2), "media_ust_por_os": round(sum(vals) / len(vals), 2),
                      "minimo": min(vals), "maximo": max(vals)})
    return {"fonte": rel(arquivo), "aviso": "Médias calculadas só com dados históricos informados; não são estimativa contratual.", "linhas": saida}


# ------------------------------------------------------------------ relatórios

def _git_periodo(inicio: str, fim: str, caminho: str) -> list[dict]:
    fmt = "%H%x1f%an%x1f%aI%x1f%s"
    off = datetime.now(TZ).strftime("%z")
    off = f"{off[:3]}:{off[3:]}"
    out = git("log", f"--since={inicio}T00:00:00{off}", f"--until={fim}T23:59:59{off}", f"--pretty=format:{fmt}", "--", caminho)
    commits = []
    for linha in filter(None, out.splitlines()):
        sha, an, dt, s = linha.split("\x1f")
        n = git("show", "--stat", "--pretty=format:", sha, "--", caminho).strip().splitlines()
        commits.append({"sha": sha, "autor": an, "data": dt, "mensagem": s, "resumo": n[-1].strip() if n else ""})
    return commits


def relatorio(cid: str, tipo: str, ref: str | None = None, profissional: str | None = None) -> Path:
    cdir = dir_contrato(cid)
    contrato = ler_yaml(cdir / "contrato.yaml")
    ref = ref or hoje()
    d0 = date.fromisoformat(ref)
    if tipo == "diario":
        ini = fim = d0
    elif tipo == "semanal":
        ini = d0 - timedelta(days=d0.weekday()); fim = ini + timedelta(days=6)
    elif tipo in ("mensal", "profissional"):
        ini = d0.replace(day=1); fim = (ini + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    else:
        raise ErroFabrica(f"tipo de relatório inválido: {tipo}")
    inis, fims = ini.isoformat(), fim.isoformat()
    oss = [ler_yaml(p) for p in sorted((cdir / "os").glob("*.yaml"))]
    tarefas = [t for t in carregar_tarefas()["tarefas"] if t["contrato"] == cid]
    no_periodo = lambda s: inis <= s[:10] <= fims  # noqa: E731
    mov = [(t, h) for t in tarefas for h in t["historico"] if no_periodo(h["em"])]
    msgs = []
    if (COM / "AGENT_MESSAGES.jsonl").exists():
        for l in (COM / "AGENT_MESSAGES.jsonl").read_text(encoding="utf-8").splitlines():
            m = json.loads(l)
            if no_periodo(m["em"]) and (not m["tarefa"] or m["tarefa"] in {t["id"] for t in tarefas}):
                msgs.append(m)
    partic, erros_p = carregar_participacoes(cid)
    partic = [p for p in partic if inis <= p["data"] <= fims and (not profissional or p["profissional_id"] == profissional)]
    profs = {p["id"]: p for p in carregar_profissionais(cid)}
    org = (contrato.get("contratante") or {}).get("orgao", "")
    num = (contrato.get("contrato") or {}).get("numero", cid)
    titulo = {"diario": f"Relatório diário — {inis}", "semanal": f"Relatório semanal — {inis} a {fims}",
              "mensal": f"Relatório mensal — {ini.strftime('%m/%Y')}",
              "profissional": f"Relatório por profissional — {profissional} — {ini.strftime('%m/%Y')}"}[tipo]
    L = [f"# {titulo}", "", f"- Órgão: {org or 'a cadastrar'}", f"- Contrato: {num}",
         f"- Ordens de serviço: {', '.join(o['os'] for o in oss) or '—'}", f"- Período: {inis} a {fims}",
         f"- Gerado em: {agora()} por G19 (Gerador de Relatórios) via `fabrica.py relatorio`", "",
         "> Este relatório contém somente fatos registrados (git, quadro de tarefas, execuções de testes, registros humanos). Itens sem registro aparecem como \"sem registro\".", ""]
    resumo_cod, resumo_test, resumo_med = [], [], []
    for o in oss:
        commits = _git_periodo(inis, fims, o["projeto"])
        resumo_cod.append((o, commits))
        for m in o["modulos"]:
            tj = ler_json(dir_mod(cid, o["os"], m["id"]) / "TESTES.json")
            if tj and no_periodo(tj["executado_em"]):
                resumo_test.append((o["os"], m, tj))
        med = ler_json(cdir / "medicoes" / f"{o['os']}.json")
        if med:
            resumo_med.append(med)
    # Resumo executivo
    ncommits = sum(len(c) for _, c in resumo_cod)
    ntest = sum(t["resumo"]["testes"] for *_, t in resumo_test)
    nfalha = sum(t["resumo"]["falhas"] + t["resumo"]["erros"] for *_, t in resumo_test)
    L += ["## Resumo executivo", "",
          f"- Commits no período: {ncommits}",
          f"- Execuções de teste registradas: {len(resumo_test)} módulo(s), {ntest} testes, {nfalha} falhas/erros",
          f"- Movimentações no quadro: {len(mov)} · Mensagens entre agentes: {len(msgs)}",
          f"- Participações humanas registradas: {len(partic)}"]
    for med in resumo_med:
        t = med["totais"]
        L.append(f"- Medição {med['os']}: previsto {t['previsto']:g} · comprovado {t['comprovado']:g} · aceito {t['aceito']:g}"
                 + (f" — {med['aviso']}" if med.get("aviso") else ""))
    L += ["", "## Profissionais designados", ""]
    if profs:
        L += ["| ID | Nome | Função |", "|---|---|---|", *[f"| {p['id']} | {p['nome']} | {p['funcao']} |" for p in profs.values()]]
    else:
        L.append("Sem registro — nenhum profissional cadastrado em PROFISSIONAIS.csv.")
    L += ["", "## Participação humana registrada", ""]
    if partic:
        L += ["| Data | Profissional | Tipo | OS/Módulo | Descrição | Evidência |", "|---|---|---|---|---|---|"]
        L += [f"| {p['data']} | {p['profissional_id']} | {p['tipo']} | {p['os']}/{p['modulo']} | {p['descricao']} | {p['evidencia']} |" for p in partic]
    else:
        L.append("Sem registro.")
    if erros_p:
        L += ["", "Registros rejeitados (corrigir):", *[f"- {e}" for e in erros_p]]
    L += ["", "## Agentes e atividades (quadro de tarefas)", ""]
    if mov:
        L += ["| Momento | Tarefa | Agente | De → Para | Por | Nota |", "|---|---|---|---|---|---|"]
        L += [f"| {h['em'][:16]} | {t['id']} {t['descricao'][:50]} | {t['agente']} | {h['de'] or '—'} → {h['para']} | {h['por']} | {h['nota']} |" for t, h in mov]
    else:
        L.append("Sem registro.")
    L += ["", "## Código produzido (git)", ""]
    for o, commits in resumo_cod:
        L.append(f"### {o['os']} — `{o['projeto']}`")
        L += [f"- `{c['sha'][:10]}` {c['data'][:16]} {c['autor']}: {c['mensagem']} ({c['resumo']})" for c in commits] or ["- Sem commits no período."]
        L.append("")
    L += ["## Testes executados", ""]
    if resumo_test:
        L += ["| OS | Módulo | Testes | Falhas/erros | Situação | Log |", "|---|---|---|---|---|---|"]
        for osid, m, t in resumo_test:
            logs = ", ".join(f"`{e['log']}`" for e in t["execucoes"])
            L.append(f"| {osid} | {m['id']} {m['nome']} | {t['resumo']['testes']} | {t['resumo']['falhas'] + t['resumo']['erros']} | {t['situacao']} | {logs} |")
    else:
        L.append("Sem registro.")
    L += ["", "## Evidências e auditoria", ""]
    for o in oss:
        a = ler_json(cdir / "evidencias" / o["os"] / "AUDITORIA.json")
        if a:
            for m in a["modulos"]:
                L.append(f"- {o['os']} {m['modulo']}: técnico {m['tecnico']}, pendências humanas {len(m['pendencias_humanas'])} — `contratos/{cid}/evidencias/{o['os']}/{m['modulo']}/`")
        else:
            L.append(f"- {o['os']}: auditoria não executada.")
    L += ["", "## Medição", ""]
    for med in resumo_med:
        L += [f"Ver `contratos/{cid}/medicoes/{med['os']}.md` (gerada em {med['medido_em']})."]
    if not resumo_med:
        L.append("Sem registro.")
    L += ["", "## Revisões e aprovações", ""]
    aprov = [p for p in partic if p["tipo"] in ("REVISAO", "APROVACAO")]
    L += [f"- {p['data']} {p['profissional_id']} {p['tipo']}: {p['descricao']} ({p['evidencia']})" for p in aprov] or ["- Nenhuma revisão/aprovação humana registrada no período."]
    L += ["", "## Pendências e bloqueios", ""]
    pend = [t for t in tarefas if t["status"] != "DONE"]
    L += [f"- {t['id']} [{t['status']}] {t['agente']}: {t['descricao']}" for t in pend] or ["- Nenhuma tarefa pendente no quadro."]
    if (COM / "AGENT_BLOCKERS.md").exists():
        L.append(f"- Bloqueios: ver `fabrica/comunicacao/AGENT_BLOCKERS.md`")
    L += ["", "## Riscos", "", "- Ver seção de riscos do GEC e bloqueios registrados.", "",
          "## Próximas atividades", ""]
    prox = [t for t in tarefas if t["status"] in ("READY", "BACKLOG")]
    L += [f"- {t['id']} ({t['prioridade']}) {t['agente']}: {t['descricao']}" for t in prox[:15]] or ["- Definir no planejamento do próximo ciclo."]
    L.append("")
    sub = {"diario": "diarios", "semanal": "semanais", "mensal": "mensais", "profissional": "profissionais"}[tipo]
    nome = {"diario": inis, "semanal": f"semana-{inis}", "mensal": ini.strftime("%Y-%m"),
            "profissional": f"{profissional}-{ini.strftime('%Y-%m')}"}[tipo]
    p = cdir / "relatorios" / sub / f"{nome}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(L), encoding="utf-8")
    return p


# -------------------------------------------------------------------- entrega

PASTAS_ENTREGA = ["01_EDITAL_CONTRATO", "02_PLANO_GEC", "03_EQUIPE_REAL", "04_AGENTES", "05_CODIGO_FONTE",
                  "06_BANCO_DE_DADOS", "07_INFRAESTRUTURA", "08_TESTES", "09_SEGURANCA_LGPD",
                  "10_EVIDENCIAS_POR_MODULO", "11_MEDICOES_UST_PF", "12_RELATORIOS_DIARIOS", "13_DOCUMENTACAO",
                  "14_PREVIEW", "15_MANUAL_PUBLICACAO", "16_PLANO_CONTINUIDADE", "17_HOMOLOGACAO",
                  "18_HISTORICO_COMMITS", "19_CHECKLIST_100", "20_RELATORIO_FINAL"]


def preparar_entrega(cid: str, osid: str) -> Path:
    o = carregar_os(cid, osid)
    cdir = dir_contrato(cid)
    proj = o["_dir_projeto"]
    base = cdir / "entregas" / osid / "ENTREGA_CONTRATO"
    if base.exists():
        shutil.rmtree(base)
    for p in PASTAS_ENTREGA:
        (base / p).mkdir(parents=True)

    def cp(src: Path, dst: str) -> None:
        if src.is_dir():
            shutil.copytree(src, base / dst / src.name, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("node_modules", "dist", "__pycache__", ".pytest_cache", "*.pyc"))
        elif src.exists():
            shutil.copy2(src, base / dst / src.name)

    for f in ["contrato.yaml", "MATRIZ_RASTREABILIDADE.md", "documentos", f"os/{osid}.yaml", "TABELA_UST.csv"]:
        cp(cdir / f, "01_EDITAL_CONTRATO")
    cp(cdir / "GEC.md", "02_PLANO_GEC")
    cp(cdir / "PROFISSIONAIS.csv", "03_EQUIPE_REAL"); cp(cdir / "PARTICIPACOES.csv", "03_EQUIPE_REAL")
    cp(FAB / "agentes" / "registry.yaml", "04_AGENTES"); cp(RAIZ / ".claude" / "agents", "04_AGENTES")
    arq = base / "05_CODIGO_FONTE" / f"{proj.name}-codigo-fonte.zip"
    git("archive", "--format=zip", "-o", str(arq), "HEAD", o["projeto"])
    for f in ["backend/migrations", "backend/app/models.py", "infra/scripts"]:
        cp(proj / f, "06_BANCO_DE_DADOS")
    for f in ["docker-compose.yml", "docker-compose.prod.yml", "infra", "backend/Dockerfile", "frontend/Dockerfile", ".env.example"]:
        cp(proj / f, "07_INFRAESTRUTURA")
    cp(RAIZ / ".github" / "workflows", "07_INFRAESTRUTURA")
    for m in o["modulos"]:
        d = dir_mod(cid, osid, m["id"])
        shutil.copytree(d / "LOGS_TESTES", base / "08_TESTES" / m["id"], dirs_exist_ok=True)
        shutil.copy2(d / "TESTES.json", base / "08_TESTES" / m["id"] / "TESTES.json") if (d / "TESTES.json").exists() else None
        shutil.copy2(d / "SEGURANCA.md", base / "09_SEGURANCA_LGPD" / f"{m['id']}-SEGURANCA.md") if (d / "SEGURANCA.md").exists() else None
        shutil.copytree(d / "SCREENSHOTS", base / "14_PREVIEW" / m["id"], dirs_exist_ok=True)
    cp(proj / "docs" / "SEGURANCA_LGPD.md", "09_SEGURANCA_LGPD")
    cp(cdir / "evidencias" / osid, "10_EVIDENCIAS_POR_MODULO")
    cp(cdir / "medicoes", "11_MEDICOES_UST_PF")
    cp(cdir / "relatorios", "12_RELATORIOS_DIARIOS")
    cp(proj / "docs", "13_DOCUMENTACAO"); cp(proj / "README.md", "13_DOCUMENTACAO")
    cp(proj / "docs" / "PREVIEW.md", "14_PREVIEW")
    cp(proj / "docs" / "MANUAL_PUBLICACAO.md", "15_MANUAL_PUBLICACAO")
    cp(proj / "docs" / "PLANO_CONTINUIDADE.md", "16_PLANO_CONTINUIDADE")
    for m in o["modulos"]:
        a = dir_mod(cid, osid, m["id"]) / "ACEITE.md"
        if a.exists():
            shutil.copy2(a, base / "17_HOMOLOGACAO" / f"{m['id']}-ACEITE.md")
    (base / "18_HISTORICO_COMMITS" / "git-log.txt").write_text(
        git("log", "--stat", "--", o["projeto"]), encoding="utf-8")
    ck = checklist(cid, osid)
    cp(cdir / "checklist" / f"{osid}.md", "19_CHECKLIST_100"); cp(cdir / "checklist" / f"{osid}.json", "19_CHECKLIST_100")
    med = ler_json(cdir / "medicoes" / f"{osid}.json") or {"totais": {}}
    aud = ler_json(cdir / "evidencias" / osid / "AUDITORIA.json") or {"modulos": []}
    final = [f"# Relatório final — {osid}", "", f"Gerado em {agora()}.", "",
             f"- Situação da entrega (checklist): **{ck['situacao_entrega']}**",
             f"- Controles: {ck['contagem']}",
             f"- Medição: {med['totais']}", "", "## Módulos", "",
             *[f"- {m['modulo']} {m['nome']}: técnico {m['tecnico']}; pendências humanas: {', '.join(p['item'] for p in m['pendencias_humanas']) or 'nenhuma'}" for m in aud["modulos"]],
             "", "## O que NÃO está comprovado", "",
             *[f"- {c}: controle crítico aguardando verificação humana" for c in ck["criticos_nao_verificados"]],
             "", "Aprovação técnica automatizada não é aceite formal do contratante.", ""]
    (base / "20_RELATORIO_FINAL" / "RELATORIO_FINAL.md").write_text("\n".join(final), encoding="utf-8")
    manifesto = []
    for p in sorted(base.rglob("*")):
        if p.is_file():
            manifesto.append({"arquivo": str(p.relative_to(base)), "bytes": p.stat().st_size,
                              "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    gravar_json(base / "MANIFESTO.json", {"gerado_em": agora(), "arquivos": manifesto})
    z = base.parent / f"ENTREGA_{cid}_{osid}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(base.rglob("*")):
            if p.is_file():
                zf.write(p, Path("ENTREGA_CONTRATO") / p.relative_to(base))
    shutil.copy2(base / "MANIFESTO.json", cdir / "entregas" / osid / "MANIFESTO.json")
    return z


# ----------------------------------------------------------------- painel / iniciar

def painel() -> str:
    q = carregar_tarefas()
    L = ["# Painel geral da Fábrica", "", f"Atualizado em {agora()}", ""]
    contratos = sorted(p.name for p in CONTRATOS.iterdir() if p.is_dir()) if CONTRATOS.exists() else []
    L.append(f"Contratos: {len(contratos)}")
    for c in contratos:
        oss = sorted((CONTRATOS / c / "os").glob("*.yaml"))
        L.append(f"- {c}: OS {', '.join(p.stem for p in oss) or '—'}")
        for p in oss:
            med = ler_json(CONTRATOS / c / "medicoes" / f"{p.stem}.json")
            ck = ler_json(CONTRATOS / c / "checklist" / f"{p.stem}.json")
            if med:
                L.append(f"  - medição: {med['totais']}")
            if ck:
                L.append(f"  - checklist: {ck['situacao_entrega']} {ck['contagem']}")
    L += ["", "Tarefas por status:"]
    for s in ESTADOS:
        L.append(f"- {s}: {sum(1 for t in q['tarefas'] if t['status'] == s)}")
    bloq = [t for t in q["tarefas"] if t["status"] == "BLOCKED"]
    if bloq:
        L += ["", "Bloqueadas:", *[f"- {t['id']} {t['agente']}: {t['historico'][-1]['nota']}" for t in bloq]]
    return "\n".join(L)


def iniciar() -> list[tuple[str, bool, str]]:
    checks = []
    def ok(nome, cond, det=""):
        checks.append((nome, bool(cond), det))
    ok("CLAUDE.md", (RAIZ / "CLAUDE.md").exists())
    ok("AGENTS.md", (RAIZ / "AGENTS.md").exists())
    prob = verificar_agentes()
    ok("40 agentes (20 G + 20 E) gerados e válidos", not prob, "; ".join(prob[:3]))
    skills = sorted(p.parent.name for p in (RAIZ / ".claude" / "skills").glob("*/SKILL.md"))
    ok("skills internas (comandos operacionais)", len(skills) >= 12, ", ".join(skills))
    for f in ("AGENT_TASKS.json", "AGENT_MESSAGES.jsonl", "AGENT_DECISIONS.md", "AGENT_HANDOFFS.md", "AGENT_BLOCKERS.md"):
        ok(f"comunicação: {f}", (COM / f).exists())
    erros = validar_quadro()
    ok("quadro de tarefas consistente", not erros, "; ".join(erros[:3]))
    ok("checklist com 100 controles", sum(len(g["controles"]) for g in ler_yaml(FAB / "qualidade" / "checklist_100.yaml")["grupos"]) == 100)
    for t in ("git", "python3", "node", "npm", "docker", "psql"):
        ok(f"ferramenta: {t}", shutil.which(t), shutil.which(t) or "não encontrada")
    r = subprocess.run(["docker", "info"], capture_output=True, text=True) if shutil.which("docker") else None
    ok("docker daemon acessível", r is not None and r.returncode == 0, "" if r and r.returncode == 0 else "daemon indisponível")
    return checks


# ------------------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="fabrica", description="Fábrica de Software Governamental — CLI")
    sp = ap.add_subparsers(dest="cmd", required=True)

    sp.add_parser("iniciar", help="INICIAR FÁBRICA: verifica configuração e ferramentas")
    sp.add_parser("painel", help="Painel geral do Diretor")

    ag = sp.add_parser("agentes").add_subparsers(dest="sub", required=True)
    ag.add_parser("gerar"); ag.add_parser("verificar"); ag.add_parser("listar")

    ct = sp.add_parser("contrato").add_subparsers(dest="sub", required=True)
    x = ct.add_parser("novo", help="NOVO CONTRATO"); x.add_argument("id")
    x = ct.add_parser("faltantes", help="Campos ainda não preenchidos do formulário"); x.add_argument("id")

    tf = sp.add_parser("tarefas").add_subparsers(dest="sub", required=True)
    x = tf.add_parser("criar")
    x.add_argument("--agente", required=True); x.add_argument("--descricao", required=True)
    x.add_argument("--prioridade", default="MEDIA"); x.add_argument("--contrato", default="")
    x.add_argument("--os", default=""); x.add_argument("--modulo", default="")
    x.add_argument("--dep", action="append", default=[]); x.add_argument("--arquivo", action="append", default=[])
    x.add_argument("--prazo", default=""); x.add_argument("--profissional", default=""); x.add_argument("--por", default="G14")
    x = tf.add_parser("mover")
    x.add_argument("id"); x.add_argument("para"); x.add_argument("--por", required=True)
    x.add_argument("--nota", default=""); x.add_argument("--resultado", default="")
    x.add_argument("--evidencia", action="append", default=[])
    x = tf.add_parser("listar"); x.add_argument("--agente"); x.add_argument("--status"); x.add_argument("--contrato")
    tf.add_parser("validar")

    x = sp.add_parser("msg"); x.add_argument("--de", required=True); x.add_argument("--para", required=True)
    x.add_argument("--texto", required=True); x.add_argument("--tarefa", default=""); x.add_argument("--tipo", default="INFO")
    for nome in ("decisao", "handoff", "bloqueio"):
        x = sp.add_parser(nome); x.add_argument("--por", required=True); x.add_argument("--texto", required=True)
        x.add_argument("--titulo", default=""); x.add_argument("--tarefa", default="")
        if nome == "handoff":
            x.add_argument("--para", required=True)

    ev = sp.add_parser("evidencias").add_subparsers(dest="sub", required=True)
    for nome in ("preparar", "commits"):
        x = ev.add_parser(nome); x.add_argument("contrato"); x.add_argument("os")
    ts = sp.add_parser("testes").add_subparsers(dest="sub", required=True)
    x = ts.add_parser("executar", help="EXECUTAR TESTES / VERIFICAR CÓDIGO"); x.add_argument("contrato"); x.add_argument("os"); x.add_argument("--modulo")

    for nome, h in (("auditar", "AUDITAR EVIDÊNCIAS"), ("medir", "MEDIR PRODUÇÃO"), ("checklist", "100 controles"), ("entrega", "PREPARAR ENTREGA")):
        x = sp.add_parser(nome, help=h); x.add_argument("contrato"); x.add_argument("os")

    x = sp.add_parser("relatorio", help="RELATÓRIO DIÁRIO/SEMANAL/MENSAL/PROFISSIONAL")
    x.add_argument("tipo", choices=["diario", "semanal", "mensal", "profissional"]); x.add_argument("contrato")
    x.add_argument("--data"); x.add_argument("--profissional")

    pr = sp.add_parser("producao").add_subparsers(dest="sub", required=True)
    x = pr.add_parser("estatisticas", help="Média de UST aceita por profissional/complexidade"); x.add_argument("arquivo")

    a = ap.parse_args(argv)
    try:
        if a.cmd == "iniciar":
            falhas = 0
            for nome, ok_, det in iniciar():
                print(f"[{'OK ' if ok_ else 'PENDENTE'}] {nome}{' — ' + det if det else ''}")
                falhas += not ok_
            print(f"\n{falhas} pendência(s).")
        elif a.cmd == "painel":
            print(painel())
        elif a.cmd == "agentes":
            if a.sub == "gerar":
                print(f"{len(gerar_agentes())} agentes gerados em .claude/agents/")
            elif a.sub == "verificar":
                prob = verificar_agentes(); print("\n".join(prob) or "OK: agentes válidos"); return 1 if prob else 0
            else:
                for ag_ in carregar_registro()["agentes"]:
                    print(f"{ag_['id']}  {ag_['slug']:32} {ag_['nome']}")
        elif a.cmd == "contrato":
            if a.sub == "novo":
                print(f"criado: {rel(novo_contrato(a.id))}")
            else:
                f = campos_faltantes(a.id); print("\n".join(f) or "formulário completo"); print(f"\n{len(f)} campo(s) faltando")
        elif a.cmd == "tarefas":
            if a.sub == "criar":
                t = criar_tarefa(agente=a.agente, descricao=a.descricao, prioridade=a.prioridade, contrato=a.contrato,
                                 os_=a.os, modulo=a.modulo, dependencias=a.dep, arquivos=a.arquivo, prazo=a.prazo,
                                 profissional=a.profissional, por=a.por)
                print(t["id"])
            elif a.sub == "mover":
                t = mover_tarefa(a.id, a.para, por=a.por, nota=a.nota, resultado=a.resultado, evidencias=a.evidencia)
                print(f"{t['id']} -> {t['status']}")
            elif a.sub == "listar":
                for t in carregar_tarefas()["tarefas"]:
                    if (a.agente and t["agente"] != a.agente) or (a.status and t["status"] != a.status) or (a.contrato and t["contrato"] != a.contrato):
                        continue
                    print(f"{t['id']} [{t['status']:11}] {t['agente']} {t['prioridade']:7} {t['modulo']:8} {t['descricao']}")
            else:
                e = validar_quadro(); print("\n".join(e) or "OK: quadro consistente"); return 1 if e else 0
        elif a.cmd == "msg":
            registrar_msg(a.de, a.para, a.texto, a.tarefa, a.tipo); print("mensagem registrada")
        elif a.cmd in ("decisao", "handoff", "bloqueio"):
            arquivo, pref = {"decisao": ("AGENT_DECISIONS.md", "D"), "handoff": ("AGENT_HANDOFFS.md", "H"), "bloqueio": ("AGENT_BLOCKERS.md", "B")}[a.cmd]
            corpo = (f"- Tarefa: {a.tarefa or '—'}\n" + (f"- Para: {a.para}\n" if a.cmd == "handoff" else "") + f"\n{a.texto}")
            ident = _anexar_md(arquivo, pref, a.titulo or a.texto[:60], corpo, a.por)
            if a.cmd == "bloqueio" and a.tarefa:
                mover_tarefa(a.tarefa, "BLOCKED", por=a.por, nota=f"{ident}: {a.texto}")
            print(ident)
        elif a.cmd == "evidencias":
            if a.sub == "preparar":
                print(f"{len(preparar_evidencias(a.contrato, a.os))} arquivo(s) de modelo criados")
            else:
                print(coletar_commits(a.contrato, a.os))
        elif a.cmd == "testes":
            for mid, r in executar_testes(a.contrato, a.os, a.modulo).items():
                print(f"{mid}: {r['situacao']} {r['resumo']}")
        elif a.cmd == "auditar":
            for m in auditar(a.contrato, a.os)["modulos"]:
                print(f"{m['modulo']}: técnico {m['tecnico']} · pendências humanas {len(m['pendencias_humanas'])} · achados {len(m['achados'])}")
        elif a.cmd == "medir":
            print(json.dumps(medir(a.contrato, a.os)["totais"], ensure_ascii=False))
        elif a.cmd == "checklist":
            r = checklist(a.contrato, a.os); print(r["situacao_entrega"], r["contagem"])
        elif a.cmd == "entrega":
            print(rel(preparar_entrega(a.contrato, a.os)))
        elif a.cmd == "relatorio":
            if a.tipo == "profissional" and not a.profissional:
                raise ErroFabrica("relatório por profissional exige --profissional")
            print(rel(relatorio(a.contrato, a.tipo, a.data, a.profissional)))
        elif a.cmd == "producao":
            print(json.dumps(estatisticas_producao(Path(a.arquivo)), ensure_ascii=False, indent=2))
    except ErroFabrica as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
