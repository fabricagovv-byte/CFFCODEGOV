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
import unicodedata
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


def brl(v: float | None) -> str:
    """Formato monetário brasileiro: 7800 -> 'R$ 7.800,00'."""
    if v is None:
        return "—"
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def slug(texto: str) -> str:
    """'Gestão Documental' -> 'gestao-documental'."""
    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(RAIZ))
    except ValueError:
        return str(p)


# ------------------------------------------------------------------ Word

def exportar_word(md: Path, cid: str | None = None, periodo: str = "", classificacao: str = "Uso interno",
                  subtitulo: str = "", saida: Path | None = None, capa: bool = True) -> Path | None:
    """Gera a versão Word (.docx) de um documento Markdown da fábrica (capa, cabeçalho, rodapé, tabelas).

    Desligue com FABRICA_WORD=0. Sem Node/biblioteca docx, avisa e segue (o .md continua valendo)."""
    if os.environ.get("FABRICA_WORD", "1") == "0":
        return None
    meta = {"periodo": periodo, "classificacao": classificacao, "subtitulo": subtitulo, "gerado_em": agora()[:16].replace("T", " "),
            "sem_capa": not capa}
    if cid and (CONTRATOS / cid / "contrato.yaml").exists():
        c = ler_yaml(CONTRATOS / cid / "contrato.yaml") or {}
        meta["orgao"] = (c.get("contratante") or {}).get("orgao", "")
        meta["contrato"] = (c.get("contrato") or {}).get("numero", "") or cid
    saida = saida or md.with_suffix(".docx")
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)
    try:
        r = subprocess.run(["node", str(FAB / "ferramentas" / "word.cjs"), str(md), str(saida), f.name],
                           capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        print("aviso: Node.js não encontrado; versão Word não gerada", file=sys.stderr)
        return None
    finally:
        os.unlink(f.name)
    if r.returncode != 0:
        print(f"aviso: versão Word não gerada ({r.stderr.strip()[:200]})", file=sys.stderr)
        return None
    return saida


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
    for sub in ("os", "evidencias", "relatorios/diarios", "relatorios/mensais", "medicoes", "checklist", "rateios"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    form = (tpl / "FORMULARIO_CONTRATO.yaml").read_text(encoding="utf-8")
    (d / "contrato.yaml").write_text(form.replace("<ID_CONTRATO>", cid), encoding="utf-8")
    for nome in ("PROFISSIONAIS.csv", "PARTICIPACOES.csv", "TABELA_UST.csv", "RATEIO.yaml", "RATEIO_TOTAIS.csv", "EDITAL.yaml",
                 "PERFIS.csv", "CATALOGO_SERVICOS.csv", "PLANEJAMENTO.csv",
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


def rodar_teste(t: dict, cwd: Path, destino: Path) -> dict:
    """Executa UM comando de teste de verdade e devolve o resultado com caminhos de JUnit e log.

    t: {nome, cmd, [tipo: comando], [junit_glob: padrão relativo ao cwd], [env]}
    - padrão: o comando grava JUnit em {junit};
    - junit_glob: o comando grava vários XML (ex.: Maven surefire) e todos são lidos;
    - tipo comando: vale o código de saída (1 verificação).
    """
    destino.mkdir(parents=True, exist_ok=True)
    carimbo = datetime.now(TZ).strftime("%Y%m%dT%H%M%S")
    junit = destino / f"{t['nome']}-{carimbo}.xml"
    log = destino / f"{t['nome']}-{carimbo}.log"
    cmd = [c.replace("{junit}", str(junit)) for c in t["cmd"]]
    ini = datetime.now(TZ)
    env = {**os.environ, **{k: str(v) for k, v in (t.get("env") or {}).items()}}
    if t.get("junit_glob"):
        for velho in glob.glob(str(cwd / t["junit_glob"])):
            Path(velho).unlink()
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env, timeout=t.get("timeout", 1800))
        codigo, saida, erro = r.returncode, r.stdout, r.stderr
    except FileNotFoundError as e:
        codigo, saida, erro = 127, "", f"ferramenta não encontrada: {e}"
    except subprocess.TimeoutExpired:
        codigo, saida, erro = 124, "", "tempo esgotado"
    fim = datetime.now(TZ)
    amb = "".join(f"# {k}={mascarar(env[k])}\n" for k in ("TEST_DATABASE_URL",) if env.get(k))
    log.write_text(f"$ (cd {rel(cwd)} && {' '.join(cmd)})\n# início: {ini.isoformat()}\n"
                   f"# fim: {fim.isoformat()}\n# código de saída: {codigo}\n{amb}\n{saida}\n{erro}", encoding="utf-8")
    vazio = {"testes": 0, "falhas": 0, "erros": 1, "ignorados": 0, "casos": []}
    if t.get("tipo") == "comando":
        st = "PASSOU" if codigo == 0 else "FALHOU"
        res = {"testes": 1, "falhas": int(codigo != 0), "erros": 0, "ignorados": 0,
               "casos": [{"suite": t["nome"], "nome": " ".join(cmd), "tempo_s": (fim - ini).total_seconds(), "status": st}]}
        junit = log
    elif t.get("junit_glob"):
        arqs = sorted(glob.glob(str(cwd / t["junit_glob"])))
        if arqs:
            res = {"testes": 0, "falhas": 0, "erros": 0, "ignorados": 0, "casos": []}
            raiz = ET.Element("testsuites")
            for a in arqs:
                parcial = ler_junit(Path(a))
                for k in ("testes", "falhas", "erros", "ignorados"):
                    res[k] += parcial[k]
                res["casos"] += parcial["casos"]
                raiz.append(ET.parse(a).getroot())
            ET.ElementTree(raiz).write(junit, encoding="utf-8", xml_declaration=True)
        else:
            res = vazio
    else:
        res = ler_junit(junit) if junit.exists() else vazio
    return {"nome": t["nome"], "comando": " ".join(cmd), "cwd": rel(cwd),
            "inicio": ini.isoformat(timespec="seconds"), "fim": fim.isoformat(timespec="seconds"),
            "codigo_saida": codigo, "junit": rel(junit), "log": rel(log), **res}


def resumir_execucoes(execucoes: list[dict]) -> tuple[dict, str]:
    total = {k: sum(e[k] for e in execucoes) for k in ("testes", "falhas", "erros", "ignorados")}
    ok = execucoes and total["testes"] > 0 and total["falhas"] == 0 and total["erros"] == 0 \
        and all(e["codigo_saida"] == 0 for e in execucoes)
    return total, ("APROVADO" if ok else "REPROVADO")


def executar_testes(cid: str, osid: str, somente: str | None = None) -> dict[str, dict]:
    """Executa de fato os comandos de teste de cada módulo e grava resultados reais."""
    o = carregar_os(cid, osid)
    exigir_autorizacao(o)
    resultados = {}
    for m in o["modulos"]:
        if somente and m["id"] != somente:
            continue
        d = dir_mod(cid, osid, m["id"])
        execucoes = [rodar_teste(t, o["_dir_projeto"] / t.get("cwd", "."), d / "LOGS_TESTES") for t in m.get("testes", [])]
        total, situacao = resumir_execucoes(execucoes)
        dados = {"fonte": "execução real via fabrica.py testes executar", "modulo": m["id"],
                 "executado_em": agora(), "resumo": total, "situacao": situacao, "execucoes": execucoes}
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
    exportar_word(d / "AUDITORIA.md", cid, periodo=osid)
    return r


# -------------------------------------------------------------------- medição

FORMULAS = ("UST_POR_SERVICO", "HORAS_X_FATOR", "HORAS")


def catalogo(cid: str) -> tuple[dict[str, list[dict]], dict[str, dict], dict]:
    """(serviços por código, perfis, medição do contrato)."""
    d = dir_contrato(cid)
    cat: dict[str, list[dict]] = {}
    if (d / "CATALOGO_SERVICOS.csv").exists():
        for r in ler_tabela(d / "CATALOGO_SERVICOS.csv"):
            cat.setdefault(r["codigo"], []).append(r)
    perfis = {r["perfil"]: r for r in ler_tabela(d / "PERFIS.csv")} if (d / "PERFIS.csv").exists() else {}
    med = (ler_yaml(d / "contrato.yaml") or {}).get("medicao") or {}
    return cat, perfis, med


def calcular_servicos(cid: str, servicos: list[dict]) -> dict:
    """Horas por perfil, quantidade medida e valor de uma lista [{codigo, quantidade}] pela fórmula DO CONTRATO."""
    cat, perfis, med = catalogo(cid)
    formula = str(med.get("formula") or "").upper()
    if formula not in FORMULAS:
        raise ErroFabrica(f"{cid}: defina medicao.formula no contrato.yaml ({' | '.join(FORMULAS)}) conforme o edital — "
                          "a fábrica não converte horas/UST sem a fórmula do contrato")
    horas: dict[str, float] = {}
    ust = valor = 0.0
    memoria = []
    for s in servicos:
        linhas = cat.get(s["codigo"])
        if not linhas:
            raise ErroFabrica(f"serviço {s['codigo']} não existe no CATALOGO_SERVICOS.csv")
        q = float(s.get("quantidade", 1) or 1)
        for ln in linhas:
            h = float(numero(ln.get("horas")) or 0) * q
            perfil = ln["perfil"]
            horas[perfil] = horas.get(perfil, 0) + h
            pf = perfis.get(perfil)
            if formula == "HORAS_X_FATOR":
                if not pf or numero(pf.get("fator_ust_por_hora")) is None:
                    raise ErroFabrica(f"perfil {perfil} sem fator_ust_por_hora em PERFIS.csv")
                ust += h * float(numero(pf["fator_ust_por_hora"]))
            elif formula == "UST_POR_SERVICO":
                ust += float(numero(ln.get("ust")) or 0) * q
            if pf and numero(pf.get("valor_hora")) is not None:
                valor += h * float(numero(pf["valor_hora"]))
        memoria.append(f"{s['codigo']} × {q:g} ({linhas[0]['servico']}; {linhas[0].get('referencia', '')})")
    total_h = sum(horas.values())
    quantidade = total_h if formula == "HORAS" else ust
    if not valor and numero(med.get("valor_unitario")) is not None:
        valor = quantidade * float(numero(med["valor_unitario"]))
    return {"formula": formula, "horas_por_perfil": {k: round(v, 2) for k, v in horas.items()}, "horas": round(total_h, 2),
            "quantidade": round(quantidade, 2), "valor": round(valor, 2), "memoria": "; ".join(memoria)}


def medir(cid: str, osid: str) -> dict:
    """Memória de cálculo: previsto (OS), comprovado (auditoria técnica), aceito (registro humano)."""
    o = carregar_os(cid, osid)
    tab = tabela_ust(cid)
    aud = {m["modulo"]: m for m in auditar(cid, osid)["modulos"]}
    itens = []
    for m in o["modulos"]:
        calc = None
        if m.get("servicos"):  # medição por catálogo de serviços × perfis × horas (fórmula do contrato)
            calc = calcular_servicos(cid, m["servicos"])
            cod = ", ".join(s["codigo"] for s in m["servicos"])
            item = {"descricao": calc["memoria"], "unidade": "HORAS" if calc["formula"] == "HORAS" else "UST",
                    "referencia_contratual": "CATALOGO_SERVICOS.csv / PERFIS.csv"}
            prev = calc["quantidade"]
        else:
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
        horas_txt = (f" [fórmula {calc['formula']}: {calc['horas']:g} h = "
                     + ", ".join(f"{k} {v:g} h" for k, v in calc["horas_por_perfil"].items()) + f"; valor {brl(calc['valor'])}]") if calc else ""
        memoria = (f"previsto={prev:g} {item['unidade']} (OS {osid}, item {cod}){horas_txt}; "
                   f"comprovado={comprovado:g} pois auditoria técnica={a['tecnico']}"
                   f"{' (regra: integral somente com evidências completas)' if comprovado == 0 else ''}; "
                   f"aceito={aceito:g} ({'termo: ' + str(ace.get('documento')) if aceito else 'sem aceite registrado'})")
        itens.append({"modulo": m["id"], "nome": m["nome"], "item": cod,
                      "descricao_item": item["descricao"], "unidade": item["unidade"],
                      "referencia_contratual": item.get("referencia_contratual", ""),
                      "previsto": prev, "comprovado": comprovado, "aceito": aceito,
                      "evidencias": rel(dir_mod(cid, osid, m["id"])), "memoria": memoria,
                      "horas": calc["horas"] if calc else None, "horas_por_perfil": calc["horas_por_perfil"] if calc else {},
                      "valor_previsto": calc["valor"] if calc else None,
                      "responsavel": frontmatter(dir_mod(cid, osid, m["id"]) / "RESPONSAVEIS.md").get("responsavel_tecnico", "")})
    tot = {k: round(sum(i[k] for i in itens), 2) for k in ("previsto", "comprovado", "aceito")}
    if any(i["horas"] is not None for i in itens):
        tot["horas"] = round(sum(i["horas"] or 0 for i in itens), 2)
        tot["valor_previsto"] = round(sum(i["valor_previsto"] or 0 for i in itens), 2)
        hp: dict[str, float] = {}
        for i in itens:
            for k, v in i["horas_por_perfil"].items():
                hp[k] = hp.get(k, 0) + v
        tot["horas_por_perfil"] = hp
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
    if tot.get("horas_por_perfil"):
        _, perfis_, _ = catalogo(cid)
        linhas += ["", "## Horas por perfil (catálogo do contrato)", "", "| Perfil | Horas | Valor/hora | Valor previsto |", "|---|---|---|---|"]
        for k, v in tot["horas_por_perfil"].items():
            vh = numero((perfis_.get(k) or {}).get("valor_hora"))
            linhas.append(f"| {k} | {v:g} | {brl(vh)} | {brl(v * vh) if vh is not None else '—'} |")
        linhas.append(f"| **Total** | **{tot['horas']:g}** | | **{brl(tot['valor_previsto'])}** |")
    linhas += ["", "## Memória por item", "", *[f"- **{i['modulo']}**: {i['memoria']}" for i in itens],
               "", "## Regras aplicadas", "",
               "- Previsto: quantidade da OS para o item da tabela contratual.",
               "- Comprovado: igual ao previsto somente se a auditoria técnica do módulo for APROVADO (evidências completas, commits reais, testes reais sem falhas); caso contrário 0. Ajuste esta regra se o contrato prever medição parcial.",
               "- Aceito: somente com ACEITE.md em status ACEITO, com `aceito_por` e `documento` (termo do contratante). Nunca maior que o comprovado.",
               "- Conversão entre horas e UST somente pela fórmula declarada no contrato (medicao.formula) e pelos fatores de PERFIS.csv; sem fórmula, não há conversão.", ""]
    (CONTRATOS / cid / "medicoes" / f"{osid}.md").write_text("\n".join(linhas), encoding="utf-8")
    exportar_word(CONTRATOS / cid / "medicoes" / f"{osid}.md", cid, periodo=osid, subtitulo="Memória de cálculo")
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
    exportar_word(cdir / "checklist" / f"{osid}.md", cid, periodo=osid)
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


def relatorio(cid: str, tipo: str, ref: str | None = None, profissional: str | None = None,
              total_ust: float | None = None) -> Path:
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
    titulo = {"diario": f"{titulo_doc(cid, 'relatorio_diario')} — {inis}",
              "semanal": f"{titulo_doc(cid, 'relatorio_semanal')} — {inis} a {fims}",
              "mensal": f"{titulo_doc(cid, 'relatorio_mensal')} — {ini.strftime('%m/%Y')}",
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
    # Resumo executivo e indicadores
    ncommits = sum(len(c) for _, c in resumo_cod)
    ntest = sum(t["resumo"]["testes"] for *_, t in resumo_test)
    nfalha = sum(t["resumo"]["falhas"] + t["resumo"]["erros"] for *_, t in resumo_test)
    concluidas = {t["id"] for t, h in mov if h["para"] == "DONE"}
    abertas = [t for t in tarefas if t["status"] != "DONE"]
    bloqueadas = [t for t in tarefas if t["status"] == "BLOCKED"]
    sd = saldo(cid)
    un = sd["unidade"]
    fmt = lambda v: "—" if v is None else f"{v:g}"  # noqa: E731
    taxa = f"{100 * (ntest - nfalha) / ntest:.1f}%" if ntest else "—"
    L += ["## Resumo executivo", "",
          f"No período foram registrados {ncommits} commit(s), {ntest} teste(s) executado(s) ({taxa} aprovados), "
          f"{len(concluidas)} tarefa(s) concluída(s) e {len(partic)} participação(ões) humana(s). "
          f"Produção acumulada: {fmt(sd['comprovado'])} {un} comprovadas e {fmt(sd['aceito'])} {un} aceitas"
          + (f" de {fmt(sd['contratado'])} {un} contratadas (saldo oficial {fmt(sd['saldo_oficial'])} {un})." if sd["contratado"] is not None else "."),
          "", "## Indicadores do período", "",
          "| Indicador | Valor |", "|---|---|",
          f"| Commits | {ncommits} |",
          f"| Testes executados | {ntest} |",
          f"| Taxa de aprovação dos testes | {taxa} |",
          f"| Tarefas concluídas no período | {len(concluidas)} |",
          f"| Tarefas em aberto | {len(abertas)} |",
          f"| Tarefas bloqueadas | {len(bloqueadas)} |",
          f"| Participações humanas registradas | {len(partic)} |",
          f"| Mensagens entre agentes | {len(msgs)} |",
          f"| Quantidade contratada ({un}) | {fmt(sd['contratado'])} |",
          f"| Previsto em OS ({un}) | {fmt(sd['previsto'])} |",
          f"| Comprovado ({un}) | {fmt(sd['comprovado'])} |",
          f"| Aceito pelo órgão ({un}) | {fmt(sd['aceito'])} |",
          f"| Saldo oficial ({un}) | {fmt(sd['saldo_oficial'])} |",
          f"| Consumo aceito | {fmt(sd['consumo_aceito_pct'])}% |"]
    for med in resumo_med:
        if med.get("aviso"):
            L += ["", f"> {med['os']}: {med['aviso']}"]
    L += ["", "## Situação por módulo", "",
          "| OS | Módulo | Área | Previsto | Comprovado | Aceito | Auditoria | Testes (ok/total) | Responsável |",
          "|---|---|---|---|---|---|---|---|---|"]
    linhas_mod = 0
    for o in oss:
        med = {i["modulo"]: i for i in (ler_json(cdir / "medicoes" / f"{o['os']}.json") or {}).get("itens", [])}
        aud = {m["modulo"]: m for m in (ler_json(cdir / "evidencias" / o["os"] / "AUDITORIA.json") or {}).get("modulos", [])}
        for m in o["modulos"]:
            mi, ai = med.get(m["id"], {}), aud.get(m["id"], {})
            tr = ai.get("testes") or {}
            ok = tr.get("testes", 0) - tr.get("falhas", 0) - tr.get("erros", 0) - tr.get("ignorados", 0)
            L.append(f"| {o['os']} | {m['id']} {m['nome']} | {m.get('area', '—')} | {fmt(mi.get('previsto', m.get('ust_previsto')))} | "
                     f"{fmt(mi.get('comprovado'))} | {fmt(mi.get('aceito'))} | {ai.get('tecnico', 'não auditado')} | "
                     f"{ok}/{tr.get('testes', 0)} | {mi.get('responsavel') or 'a cadastrar'} |")
            linhas_mod += 1
    if not linhas_mod:
        L.append("| — | Nenhum módulo cadastrado | | | | | | | |")
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
    L += ["", "## Participação e rateio interno por profissional", ""]
    rt = rateio(cid, "mensal" if tipo == "profissional" else tipo, ref, total_ust)
    L += tabela_rateio_md(rt, profissional)
    L += ["", "## Agentes de IA no período", ""]
    if mov:
        nomes_ag = {a["id"]: a["nome"] for a in carregar_registro()["agentes"]}
        por_ag: dict[str, dict] = {}
        for t_, h in mov:
            x = por_ag.setdefault(t_["agente"], {"mov": 0, "done": set(), "tarefas": set()})
            x["mov"] += 1; x["tarefas"].add(t_["id"])
            if h["para"] == "DONE":
                x["done"].add(t_["id"])
        L += ["| Agente | Função | Tarefas tocadas | Concluídas | Movimentações |", "|---|---|---|---|---|"]
        L += [f"| {a} | {nomes_ag.get(a, '')} | {len(x['tarefas'])} | {len(x['done'])} | {x['mov']} |" for a, x in sorted(por_ag.items())]
        L.append("\nHistórico completo no Anexo A.")
    else:
        L.append("Sem registro.")
    L += ["", "## Código produzido (git)", ""]
    linhas_c = [f"| {o['os']} | `{c['sha'][:10]}` | {c['data'][:16].replace('T', ' ')} | {c['autor']} | {c['mensagem']} | {c['resumo']} |"
                for o, commits in resumo_cod for c in commits]
    L += (["| OS | Commit | Data | Autor | Descrição | Alterações |", "|---|---|---|---|---|---|", *linhas_c] if linhas_c else ["Sem commits no período."])
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
    if mov:
        L += ["", "## Anexo A — Movimentações do quadro de tarefas", "",
              "| Momento | Tarefa | Agente | De → Para | Por | Nota |", "|---|---|---|---|---|---|"]
        L += [f"| {h['em'][:16].replace('T', ' ')} | {t_['id']} {t_['descricao'][:50]} | {t_['agente']} | {h['de'] or '—'} → {h['para']} | {h['por']} | {h['nota']} |" for t_, h in mov]
    L.append("")
    sub = {"diario": "diarios", "semanal": "semanais", "mensal": "mensais", "profissional": "profissionais"}[tipo]
    nome = {"diario": inis, "semanal": f"semana-{inis}", "mensal": ini.strftime("%Y-%m"),
            "profissional": f"{profissional}-{ini.strftime('%Y-%m')}"}[tipo]
    p = cdir / "relatorios" / sub / f"{nome}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(L), encoding="utf-8")
    exportar_word(p, cid, periodo=f"{inis} a {fims}" if inis != fims else inis)
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


# ------------------------------------------------------- equipe real (CPF / LGPD)

SENIORIDADES = ["JUNIOR", "PLENO", "SENIOR", "ESPECIALISTA"]
CAMPOS_PROF = ["id", "nome", "funcao", "area", "senioridade", "cpf_mascarado", "formacao", "anos_experiencia", "certificacoes",
               "qualificacao", "registro_ou_certificacao", "responsabilidades", "modulos", "email_corporativo", "inicio", "fim"]


def so_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")


def validar_cpf(cpf: str) -> bool:
    c = so_digitos(cpf)
    if len(c) != 11 or c == c[0] * 11:
        return False
    for n in (9, 10):
        soma = sum(int(c[i]) * (n + 1 - i) for i in range(n))
        dv = (soma * 10) % 11 % 10
        if dv != int(c[n]):
            return False
    return True


def mascarar_cpf(cpf: str) -> str:
    c = so_digitos(cpf)
    return f"***.{c[3:6]}.{c[6:9]}-**" if len(c) == 11 else ""


SINONIMOS_COLUNA = {"cargo": "funcao", "funcao": "funcao", "função": "funcao", "nome completo": "nome", "nome": "nome", "cpf": "cpf",
                    "area": "area", "área": "area", "senioridade": "senioridade"}


def ler_tabela_docx(arquivo: Path) -> list[dict]:
    """Lê a primeira tabela de um .docx cujo cabeçalho tenha 'Nome' (ex.: Nome | CPF | Cargo)."""
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(arquivo) as z:
        raiz = ET.fromstring(z.read("word/document.xml"))
    for tbl in raiz.iter(f"{{{ns['w']}}}tbl"):
        linhas = [["".join(t.text or "" for t in tc.iter(f"{{{ns['w']}}}t")).strip() for tc in tr.findall("w:tc", ns)]
                  for tr in tbl.findall("w:tr", ns)]
        if not linhas:
            continue
        cab = [SINONIMOS_COLUNA.get(c.strip().lower(), c.strip().lower()) for c in linhas[0]]
        if "nome" not in cab:
            continue
        return [dict(zip(cab, ln)) for ln in linhas[1:] if any(ln) and not ln[0].startswith("#")]
    return []


def ler_tabela(arquivo: Path, aba: str | None = None) -> list[dict]:
    """Lê CSV, uma aba de XLSX ou a tabela de equipe de um DOCX como lista de dicionários."""
    if arquivo.suffix.lower() == ".docx":
        return ler_tabela_docx(arquivo) if aba in (None, "PROFISSIONAIS") else []
    if arquivo.suffix.lower() in (".xlsx", ".xlsm"):
        import openpyxl  # opcional: só para planilhas
        wb = openpyxl.load_workbook(arquivo, data_only=True, read_only=True)
        if aba not in wb.sheetnames:
            return []
        linhas = list(wb[aba].iter_rows(values_only=True))
        if not linhas:
            return []
        cab = [str(c or "").strip() for c in linhas[0]]
        dados = []
        for ln in linhas[1:]:
            reg = {cab[i]: ("" if v is None else str(v).strip()) for i, v in enumerate(ln) if i < len(cab) and cab[i]}
            if any(reg.values()) and not str(next(iter(reg.values()), "")).startswith("#"):
                dados.append(reg)
        return dados
    with open(arquivo, encoding="utf-8-sig") as f:
        return [r for r in csv.DictReader(f) if any((v or "").strip() for v in r.values())
                and not (next(iter(r.values())) or "").startswith("#")]


def gravar_csv(p: Path, campos: list[str], linhas: list[dict]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)


def importar_profissionais(cid: str, arquivo: Path) -> dict:
    """Importa a equipe (nome, função, CPF, área, senioridade...).

    O CPF completo vai SOMENTE para contratos/<ID>/privado/ (fora do git, permissão 600);
    o arquivo versionado guarda o CPF mascarado.
    """
    d = dir_contrato(cid)
    entrada = ler_tabela(arquivo, "PROFISSIONAIS")
    atuais = {p["id"]: p for p in carregar_profissionais(cid)}
    privado_arq = d / "privado" / "PROFISSIONAIS_PRIVADO.csv"
    privados = {r["id"]: r for r in ler_tabela(privado_arq)} if privado_arq.exists() else {}
    por_cpf = {so_digitos(v["cpf"]): k for k, v in privados.items() if v.get("cpf")}
    por_nome = {v["nome"].strip().lower(): k for k, v in atuais.items()}
    erros, novos = [], 0
    for n, r in enumerate(entrada, start=2):
        nome, funcao = (r.get("nome") or "").strip(), (r.get("funcao") or r.get("cargo") or "").strip()
        if not nome or not funcao:
            erros.append(f"linha {n}: nome e função são obrigatórios")
            continue
        cpf = so_digitos(r.get("cpf", ""))
        if cpf and not validar_cpf(cpf):
            erros.append(f"linha {n}: CPF inválido para {nome}")
            continue
        sen = (r.get("senioridade") or "").strip().upper()
        if sen and sen not in SENIORIDADES:
            erros.append(f"linha {n}: senioridade {sen!r} inválida (use {SENIORIDADES})")
            continue
        pid = (r.get("id") or "").strip() or por_cpf.get(cpf) or por_nome.get(nome.lower())
        if not pid:
            usados = [int(x[1:]) for x in list(atuais) if re.fullmatch(r"P\d+", x)]
            pid = f"P{max(usados or [0]) + 1:02d}"
            novos += 1
        reg = {k: (r.get(k) or "").strip() for k in CAMPOS_PROF}
        reg.update(id=pid, nome=nome, funcao=funcao, senioridade=sen, area=(r.get("area") or "").strip().upper(),
                   cpf_mascarado=mascarar_cpf(cpf))
        atuais[pid] = {**atuais.get(pid, {}), **{k: v for k, v in reg.items() if v or k in ("id", "nome", "funcao")}}
        if cpf:
            privados[pid] = {"id": pid, "nome": nome, "cpf": cpf}
            por_cpf[cpf] = pid
        por_nome[nome.lower()] = pid
    gravar_csv(d / "PROFISSIONAIS.csv", CAMPOS_PROF, sorted(atuais.values(), key=lambda x: x["id"]))
    if privados:
        privado_arq.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(privado_arq.parent, 0o700)
        gravar_csv(privado_arq, ["id", "nome", "cpf"], sorted(privados.values(), key=lambda x: x["id"]))
        os.chmod(privado_arq, 0o600)
        (privado_arq.parent / "LEIA-ME.md").write_text(
            "Dados pessoais completos (CPF). NÃO versionar, NÃO enviar por canais abertos (LGPD).\n"
            "Esta pasta está no .gitignore. Faça cópia segura fora do repositório.\n", encoding="utf-8")
    return {"importados": len(entrada) - len(erros), "novos": novos, "erros": erros, "total_equipe": len(atuais)}


def equipe_oficial(cid: str) -> Path:
    """Documento simplificado da equipe — Nome, CPF e Cargo — com CPF completo, na pasta privada (md + Word)."""
    d = dir_contrato(cid)
    arq = d / "privado" / "PROFISSIONAIS_PRIVADO.csv"
    privados = {r["id"]: r for r in ler_tabela(arq)} if arq.exists() else {}
    L = [f"# Equipe do contrato — {cid}", "",
         "> Documento com dados pessoais (CPF). Uso restrito: envio oficial ao órgão contratante. Não versionar (LGPD).", "",
         "| Nome | CPF | Cargo |", "|---|---|---|"]
    for p in carregar_profissionais(cid):
        c = so_digitos(privados.get(p["id"], {}).get("cpf", ""))
        cpf = f"{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}" if c else "não informado"
        L.append(f"| {p['nome']} | {cpf} | {p['funcao']} |")
    saida = d / "privado" / "EQUIPE_NOME_CPF_CARGO.md"
    saida.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(saida.parent, 0o700)
    saida.write_text("\n".join(L) + "\n", encoding="utf-8")
    os.chmod(saida, 0o600)
    w = exportar_word(saida, cid, classificacao="RESTRITO — dados pessoais (LGPD)", capa=False)
    if w:
        os.chmod(w, 0o600)
    return w or saida


def equipe_modelo(destino: Path, linhas: int = 25) -> Path:
    """Modelo em Word para preencher: Nome | CPF | Cargo (depois: fabrica.py profissionais importar <ID> <arquivo.docx>)."""
    import tempfile
    L = ["# Equipe — Nome, CPF e Cargo", "",
         "Preencha uma linha por pessoa. Só Nome e Cargo são obrigatórios; o CPF é usado apenas na lista oficial ao órgão "
         "e fica guardado fora do repositório (LGPD). Devolva este arquivo na conversa dizendo: IMPORTAR EQUIPE <ID do contrato>.", "",
         "| Nome | CPF | Cargo |", "|---|---|---|", *["|  |  |  |"] * linhas, ""]
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("\n".join(L))
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        if not exportar_word(Path(f.name), None, classificacao="Formulário — preencher", saida=destino, capa=False):
            raise ErroFabrica("não foi possível gerar o Word (precisa de Node.js e da biblioteca docx)")
    finally:
        os.unlink(f.name)
    return destino


# ------------------------------------------------------------- rateio interno

RATEIO_PADRAO = {
    "modo": "proporcional",  # proporcional | senior_da_area
    "pesos_tipo": {"CONDUCAO": 3, "CORRECAO": 2, "REVISAO": 1, "ORIENTACAO": 1, "APROVACAO": 1},
    "multiplicador_senioridade": {"ESPECIALISTA": 1.5, "SENIOR": 1.5, "PLENO": 1.0, "JUNIOR": 0.7, "": 1.0},
    "areas_modulos": {},
}


def periodo(tipo: str, ref: str | None) -> tuple[str, str]:
    d0 = date.fromisoformat(ref or hoje())
    if tipo == "diario":
        ini = fim = d0
    elif tipo == "semanal":
        ini = d0 - timedelta(days=d0.weekday()); fim = ini + timedelta(days=6)
    elif tipo in ("mensal", "profissional"):
        ini = d0.replace(day=1); fim = (ini + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    else:
        raise ErroFabrica(f"período inválido: {tipo}")
    return ini.isoformat(), fim.isoformat()


def total_informado(cid: str, tipo: str, inicio: str) -> dict | None:
    """Total de UST do período informado pelo usuário em RATEIO_TOTAIS.csv (ex.: 250 UST na semana)."""
    p = dir_contrato(cid) / "RATEIO_TOTAIS.csv"
    if not p.exists():
        return None
    for r in ler_tabela(p):
        if r.get("periodo") == tipo and r.get("data_inicio") == inicio and r.get("total_ust"):
            return {"total": float(str(r["total_ust"]).replace(",", ".")), "base": r.get("base", ""),
                    "documento": r.get("documento", "")}
    return None


def rateio(cid: str, tipo: str, ref: str | None = None, total: float | None = None) -> dict:
    """Divide o total do período entre os profissionais COM participação registrada, por área e senioridade.

    É atribuição gerencial interna: não altera a medição contratual nem cria participação.
    """
    d = dir_contrato(cid)
    cfg = {**RATEIO_PADRAO, **((ler_yaml(d / "RATEIO.yaml") or {}) if (d / "RATEIO.yaml").exists() else {})}
    inicio, fim = periodo(tipo, ref)
    info = {"total": total, "base": "informado na linha de comando", "documento": ""} if total is not None \
        else total_informado(cid, tipo, inicio)
    profs = {p["id"]: p for p in carregar_profissionais(cid)}
    partic, erros = carregar_participacoes(cid)
    partic = [p for p in partic if inicio <= p["data"] <= fim]
    area_mod = dict(cfg.get("areas_modulos") or {})
    for po in sorted((d / "os").glob("*.yaml")):
        for m in (ler_yaml(po) or {}).get("modulos", []):
            if m.get("area"):
                area_mod.setdefault(m["id"], str(m["area"]).upper())
    pesos, cont = {}, {}
    for p in partic:
        pr = profs[p["profissional_id"]]
        area = area_mod.get(p["modulo"]) or (pr.get("area") or "GERAL").upper()
        w = float(cfg["pesos_tipo"].get(p["tipo"], 1)) * float(cfg["multiplicador_senioridade"].get((pr.get("senioridade") or "").upper(), 1))
        chave = (area, p["profissional_id"])
        pesos[chave] = pesos.get(chave, 0) + w
        cont[chave] = cont.get(chave, 0) + 1
    soma = sum(pesos.values())
    areas = sorted({a for a, _ in pesos})
    ordem_sen = {s: i for i, s in enumerate(SENIORIDADES)}
    linhas = []
    for a in areas:
        membros = [(pid, w) for (ar, pid), w in pesos.items() if ar == a]
        peso_area = sum(w for _, w in membros)
        senior = max(membros, key=lambda x: (ordem_sen.get((profs[x[0]].get("senioridade") or "").upper(), -1), x[1], -int(re.sub(r"\D", "", x[0]) or 0)))[0]
        for pid, w in sorted(membros):
            if cfg["modo"] == "senior_da_area":
                frac = (peso_area / soma) if pid == senior else 0.0
            else:
                frac = w / soma
            linhas.append({"area": a, "profissional_id": pid, "nome": profs[pid]["nome"], "funcao": profs[pid]["funcao"],
                           "senioridade": profs[pid].get("senioridade", ""), "participacoes": cont[(a, pid)],
                           "peso": round(w, 3), "percentual": round(frac * 100, 2),
                           "ust": round(frac * info["total"], 2) if info else None,
                           "responsavel_area": pid == senior})
    r = {"contrato": cid, "periodo": tipo, "inicio": inicio, "fim": fim, "gerado_em": agora(), "modo": cfg["modo"],
         "total": info["total"] if info else None, "base_total": info["base"] if info else "",
         "documento_total": info["documento"] if info else "", "participacoes_no_periodo": len(partic),
         "registros_rejeitados": erros, "linhas": linhas,
         "nao_atribuido": (info["total"] if info else 0) if not linhas else 0,
         "aviso": "Rateio interno de atribuição gerencial. Não é medição contratual e não substitui o aceite do órgão. "
                  "Só entram profissionais com participação registrada (PARTICIPACOES.csv) no período."}
    nome = f"{tipo}-{inicio}"
    gravar_json(d / "rateios" / f"{nome}.json", r)
    (d / "rateios" / f"{nome}.md").write_text(f"# Rateio interno de UST — {tipo} — {inicio} a {fim}\n\n"
                                              + "\n".join(tabela_rateio_md(r)) + "\n", encoding="utf-8")
    return r


def tabela_rateio_md(r: dict, profissional: str | None = None) -> list[str]:
    L = [f"Período {r['inicio']} a {r['fim']} · modo **{r['modo']}** · participações registradas: {r['participacoes_no_periodo']}"]
    if r["total"] is not None:
        L.append(f"Total a dividir: **{r['total']:g} UST** (base: {r['base_total'] or 'não informada'}; documento: {r['documento_total'] or 'sem documento/assinatura'})")
    else:
        L.append("Total do período não informado (preencha RATEIO_TOTAIS.csv ou use --total): mostrando só percentuais.")
    L += ["", f"> {r['aviso']}", ""]
    linhas = [x for x in r["linhas"] if not profissional or x["profissional_id"] == profissional]
    if not linhas:
        L.append("Sem participação registrada no período — nada atribuído." + (f" Total não atribuído: {r['nao_atribuido']:g} UST." if r["nao_atribuido"] else ""))
        return L
    L += ["| Área | Profissional | Função | Senioridade | Participações | Peso | % | UST | Responsável da área |",
          "|---|---|---|---|---|---|---|---|---|"]
    for x in linhas:
        ust = "—" if x["ust"] is None else f"{x['ust']:g}"
        L.append(f"| {x['area']} | {x['profissional_id']} {x['nome']} | {x['funcao']} | {x['senioridade'] or '—'} | "
                 f"{x['participacoes']} | {x['peso']:g} | {x['percentual']:g}% | {ust} | {'sim' if x['responsavel_area'] else ''} |")
    if r["registros_rejeitados"]:
        L += ["", "Registros de participação rejeitados (corrigir):", *[f"- {e}" for e in r["registros_rejeitados"]]]
    return L


# ------------------------------------------------------------------ planilha

ABAS_PLANILHA = {
    "PROFISSIONAIS": ["nome", "funcao", "cpf", "area", "senioridade", "formacao", "anos_experiencia", "certificacoes",
                      "qualificacao", "responsabilidades", "email_corporativo", "inicio", "fim"],
    "CAPACIDADES": ["tipo", "item", "detalhe", "evidencia"],
    "PERFIS": ["perfil", "descricao", "valor_hora", "fator_ust_por_hora", "referencia"],
    "CATALOGO_SERVICOS": ["codigo", "servico", "complexidade", "perfil", "horas", "ust", "referencia"],
    "PLANEJAMENTO": ["projeto", "modulo", "nome", "area", "servico", "quantidade", "inicio", "fim", "responsavel", "prioridade", "observacao"],
    "PARTICIPACOES": ["data", "profissional_id", "os", "modulo", "tipo", "descricao", "evidencia", "horas_declaradas"],
    "TABELA_UST": ["codigo", "descricao", "unidade", "ust_por_unidade", "complexidade", "referencia_contratual", "observacao"],
    "RATEIO_TOTAIS": ["periodo", "data_inicio", "total_ust", "base", "documento"],
    "PRODUCAO_HISTORICA": ["profissional", "mes", "os", "item_tabela", "complexidade", "ust_aceita", "documento_aceite"],
    "PROJETOS": ["id", "sistema", "orgao", "contrato", "componentes", "repositorio", "responsavel_tecnico", "situacao"],
}
LISTAS = {"senioridade": SENIORIDADES, "tipo": TIPOS_PARTICIPACAO,
          "area": ["BACKEND", "FRONTEND", "DADOS", "INTEGRACOES", "INFRA", "QUALIDADE", "SEGURANCA", "GESTAO", "REQUISITOS", "UX"],
          "periodo": ["diario", "semanal", "mensal"], "base": ["aceito", "comprovado", "previsto"],
          "unidade": ["UST", "PF", "HORA", "ENTREGAVEL"],
          "tipo_cap": ["TECNOLOGIA", "CERTIFICACAO_EMPRESA", "ATESTADO", "METODOLOGIA", "INFRAESTRUTURA", "FERRAMENTA", "OUTRO"], "complexidade": ["BAIXA", "MEDIA", "ALTA", "MUITO_ALTA"]}


def _campos_formulario() -> list[tuple[str, str]]:
    """Campos (caminho.pontuado, comentário) do FORMULARIO_CONTRATO.yaml."""
    campos, pilha = [], []
    for linha in (FAB / "templates" / "FORMULARIO_CONTRATO.yaml").read_text(encoding="utf-8").splitlines():
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        ind = (len(linha) - len(linha.lstrip())) // 2
        chave, _, resto = linha.strip().partition(":")
        pilha = pilha[:ind] + [chave]
        valor, _, coment = resto.partition("#")
        if valor.strip() == "" and not coment.strip():
            continue  # grupo
        campos.append((".".join(pilha), re.sub(r"^\d+(-\d+)?\s*", "", coment.strip())))
    return campos


CAMPOS_EMPRESA = [("razao_social", "Razão social da contratada"), ("cnpj", "CNPJ"), ("endereco", "Endereço"),
                  ("responsavel_legal", "Nome do responsável legal"), ("preposto", "Nome do preposto junto ao órgão"),
                  ("contato", "E-mail/telefone de contato"), ("porte", "ME / EPP / demais"),
                  ("areas_atuacao", "Ex.: desenvolvimento, sustentação, BI"), ("observacoes", "Qualquer informação útil")]


def gerar_planilha(destino: Path) -> Path:
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "LEIA-ME"
    texto = [
        "DOCUMENTO BASE — Fábrica de Software Governamental",
        "",
        "Preencha uma vez e entregue junto com o edital: a fábrica cruza com o edital e diz o que atende, o que ajustar e o que falta.",
        "Mínimo necessário: aba PROFISSIONAIS com NOME e FUNÇÃO de cada pessoa. O resto melhora a análise.",
        "",
        "1. Preencha as abas. Linhas iniciadas por # são exemplos e são ignoradas.",
        "   EMPRESA: dados da contratada. CAPACIDADES: tecnologias, certificações, atestados, metodologias, infraestrutura.",
        "2. CONTRATO: só a coluna 'valor' (deixe vazio o que não souber).",
        "3. PROFISSIONAIS: nome, função e CPF de cada pessoa real; área e senioridade servem para o rateio.",
        "   O CPF NÃO vai para o git: fica numa pasta privada; nos relatórios aparece mascarado (***.456.789-**).",
        "4. PARTICIPACOES: o que cada pessoa fez (conduziu, corrigiu, revisou, orientou, aprovou) e a prova",
        "   (commit, PR, ata, e-mail). Sem assinatura? Escreva 'registro do gestor em AAAA-MM-DD'.",
        "5. RATEIO_TOTAIS: total de UST do período (ex.: semanal, 2026-11-02, 250) para dividir entre a equipe.",
        "6. TABELA_UST: copie o catálogo do Termo de Referência sem converter unidades.",
        "7. PROJETOS: até 30 sistemas — cada linha vira um repositório próprio.",
        "   PERFIS e CATALOGO_SERVICOS: perfis do órgão (valor/hora, fator UST) e horas de cada serviço por perfil, como no edital.",
        "   PLANEJAMENTO: o SEU plano — projeto, módulo, serviço, quantidade, início, fim, responsável. A fábrica calcula UST, horas, valor e capacidade.",
        "8. Envie este arquivo com o edital e diga: IMPORTAR DOCUMENTO BASE <ID-do-contrato> e depois CONFRONTAR EDITAL <ID>.",
    ]
    for i, t in enumerate(texto, start=1):
        ws.cell(row=i, column=1, value=t)
    ws["A1"].font = Font(bold=True, size=14)
    ws.column_dimensions["A"].width = 110
    cab_fill = PatternFill("solid", fgColor="1351B4")
    we = wb.create_sheet("EMPRESA")
    we.append(["campo", "valor", "ajuda"])
    for campo, ajuda in CAMPOS_EMPRESA:
        we.append([campo, "", ajuda])
    we.column_dimensions["A"].width = 24; we.column_dimensions["B"].width = 50; we.column_dimensions["C"].width = 50
    wc = wb.create_sheet("CONTRATO")
    wc.append(["campo", "valor", "ajuda"])
    for campo, ajuda in _campos_formulario():
        wc.append([campo, "", ajuda])
    exemplos = {
        "PROFISSIONAIS": ["#Maria Exemplo", "Desenvolvedora Backend", "000.000.000-00", "BACKEND", "SENIOR", "Ciência da Computação", "8", "Java OCP; Scrum", "", "APIs e revisão", "maria@empresa.com.br", "2026-01-01", ""],
        "CAPACIDADES": ["#TECNOLOGIA", "Java / Spring Boot", "5 sistemas em produção desde 2019", "atestado 03/2024"],
        "PERFIS": ["#DESENVOLVEDOR_PLENO", "Desenvolvedor pleno", "95.00", "1.0", "TR Anexo II tabela 3"],
        "CATALOGO_SERVICOS": ["#SRV-CRUD-M", "Cadastro média complexidade", "MEDIA", "DESENVOLVEDOR_PLENO", "16", "", "TR item 5.2"],
        "PLANEJAMENTO": ["#SGD", "MOD-101", "Cadastro de interessados", "BACKEND", "SRV-CRUD-M", "1", "2026-11-03", "2026-11-05", "P01", "ALTA", ""],
        "PARTICIPACOES": ["#2026-11-03", "P01", "OS-001", "MOD-001", "REVISAO", "Revisou e corrigiu a API de login", "PR #12", ""],
        "TABELA_UST": ["#UST-DEV-03", "Desenvolvimento alta complexidade", "UST", "24", "ALTA", "TR item 5.3", ""],
        "RATEIO_TOTAIS": ["#semanal", "2026-11-02", "250", "aceito", "Termo 12/2026 ou e-mail do fiscal"],
        "PRODUCAO_HISTORICA": ["#P01", "2026-09", "OS-014", "UST-DEV-03", "ALTA", "24", "Termo 014/2026"],
        "PROJETOS": ["#PMX-001-SGD", "Gestão Documental", "Prefeitura X", "CT-12/2026", "backend=python-fastapi;frontend=react-vite", "github.com/org/pmx-001-sgd", "P01", "PLANEJADO"],
    }
    for aba, cols in ABAS_PLANILHA.items():
        w = wb.create_sheet(aba)
        w.append(cols)
        w.append(exemplos[aba])
        for i, c in enumerate(cols, start=1):
            w.column_dimensions[openpyxl.utils.get_column_letter(i)].width = max(14, len(c) + 4)
            lista = LISTAS.get("tipo_cap" if (aba, c) == ("CAPACIDADES", "tipo") else c)
            if lista:
                dv = DataValidation(type="list", formula1='"' + ",".join(lista) + '"', allow_blank=True)
                w.add_data_validation(dv)
                col = openpyxl.utils.get_column_letter(i)
                dv.add(f"{col}3:{col}500")
    for w in wb.worksheets[1:]:
        for c in w[1]:
            c.font = Font(bold=True, color="FFFFFF"); c.fill = cab_fill; c.alignment = Alignment(wrap_text=True)
        w.freeze_panes = "A2"
    wc.column_dimensions["A"].width = 40; wc.column_dimensions["B"].width = 50; wc.column_dimensions["C"].width = 70
    destino.parent.mkdir(parents=True, exist_ok=True)
    wb.save(destino)
    return destino


def _definir(obj: dict, caminho: str, valor: Any) -> None:
    partes = caminho.split(".")
    for p in partes[:-1]:
        obj = obj.setdefault(p, {})
    atual = obj.get(partes[-1])
    if isinstance(atual, bool) or str(valor).lower() in ("true", "false", "sim", "não", "nao"):
        valor = str(valor).lower() in ("true", "sim")
    elif isinstance(atual, list):
        valor = [v.strip() for v in str(valor).split(";") if v.strip()]
    obj[partes[-1]] = valor


def importar_planilha(cid: str, arquivo: Path) -> dict:
    """Importa a planilha preenchida para o contrato (cria o contrato se não existir)."""
    if not (CONTRATOS / cid).exists():
        novo_contrato(cid)
    d = dir_contrato(cid)
    res = {}
    contrato = ler_yaml(d / "contrato.yaml") or {}
    n = 0
    for r in ler_tabela(arquivo, "CONTRATO"):
        if r.get("campo") and r.get("valor"):
            _definir(contrato, r["campo"], r["valor"]); n += 1
    if n:
        (d / "contrato.yaml").write_text("# Atualizado por fabrica.py planilha importar\n" +
                                         yaml.safe_dump(contrato, allow_unicode=True, sort_keys=False), encoding="utf-8")
    res["contrato_campos"] = n
    emp = {r["campo"]: r["valor"] for r in ler_tabela(arquivo, "EMPRESA") if r.get("campo") and r.get("valor")}
    caps = ler_tabela(arquivo, "CAPACIDADES")
    if emp or caps:
        base = carregar_base(cid)
        base["empresa"] = {**(base.get("empresa") or {}), **emp}
        if caps:
            base["capacidades"] = caps
        (d / "BASE.yaml").write_text("# Documento base importado (empresa e capacidades)\n" +
                                     yaml.safe_dump(base, allow_unicode=True, sort_keys=False), encoding="utf-8")
        res["empresa_campos"], res["capacidades"] = len(emp), len(caps)
    if ler_tabela(arquivo, "PROFISSIONAIS"):
        res["profissionais"] = importar_profissionais(cid, arquivo)
    for aba, nome in (("PARTICIPACOES", "PARTICIPACOES.csv"), ("TABELA_UST", "TABELA_UST.csv"),
                      ("RATEIO_TOTAIS", "RATEIO_TOTAIS.csv"), ("PRODUCAO_HISTORICA", "PRODUCAO_HISTORICA.csv"),
                      ("PERFIS", "PERFIS.csv"), ("CATALOGO_SERVICOS", "CATALOGO_SERVICOS.csv"), ("PLANEJAMENTO", "PLANEJAMENTO.csv"),
                      ("PROJETOS", "PROJETOS.csv")):
        linhas = ler_tabela(arquivo, aba)
        if linhas:
            gravar_csv(d / nome, ABAS_PLANILHA[aba], linhas)
            res[aba.lower()] = len(linhas)
    return res


# -------------------------------------------------------- stacks multi-linguagem

STACKS = FAB / "stacks"


def carregar_stack(sid: str) -> dict:
    p = STACKS / f"{sid}.yaml"
    if not p.exists():
        raise ErroFabrica(f"stack inexistente: {sid} (disponíveis: {', '.join(listar_stacks())})")
    return ler_yaml(p)


def listar_stacks() -> list[str]:
    return sorted(p.stem for p in STACKS.glob("*.yaml"))


def criar_componente(stack: str, destino: Path, nome: str) -> Path:
    """Copia o esqueleto (scaffold) da stack para o destino, trocando {{NOME}}."""
    st = carregar_stack(stack)
    origem = STACKS / stack
    if destino.exists() and any(destino.iterdir()):
        raise ErroFabrica(f"destino não está vazio: {destino}")
    shutil.copytree(origem, destino, dirs_exist_ok=True)
    sl = slug(nome) or "app"
    for p in destino.rglob("*"):
        if p.is_file():
            try:
                t = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if "{{" in t:
                p.write_text(t.replace("{{NOME}}", nome).replace("{{SLUG_RUST}}", sl.replace("-", "_")).replace("{{SLUG}}", sl), encoding="utf-8")
    return destino


def verificar_componente(stack: str, caminho: Path, destino_logs: Path, instalar: bool = True) -> dict:
    st = carregar_stack(stack)
    execs = []
    if instalar and st["comandos"].get("instalar"):
        execs.append(rodar_teste({"nome": f"{stack}-instalar", "tipo": "comando", "cmd": st["comandos"]["instalar"],
                                  "timeout": 1800}, caminho, destino_logs))
        if execs[-1]["codigo_saida"] != 0:
            total, sit = resumir_execucoes(execs)
            return {"stack": stack, "situacao": sit, "resumo": total, "execucoes": execs}
    teste = {**st["comandos"]["testar"], "nome": f"{stack}-testes"}
    execs.append(rodar_teste(teste, caminho, destino_logs))
    if st["comandos"].get("build"):
        execs.append(rodar_teste({"nome": f"{stack}-build", "tipo": "comando", "cmd": st["comandos"]["build"]}, caminho, destino_logs))
    total, sit = resumir_execucoes(execs)
    return {"stack": stack, "situacao": sit, "resumo": total, "execucoes": execs}


def verificar_stacks(somente: list[str] | None = None, ignorar: dict[str, str] | None = None) -> Path:
    """Cria cada esqueleto num diretório temporário, instala, testa e registra o resultado REAL."""
    import tempfile
    linhas = ["# Verificação das stacks", "", f"Executado em {agora()} por `fabrica.py stacks verificar` (instala dependências e roda os testes de cada esqueleto).", "",
              "| Stack | Linguagem | Situação | Verificações (instalar + testes + build) | Detalhe |", "|---|---|---|---|---|"]
    resultados = {}
    logs = FAB / "stacks" / "_verificacao"
    for sid in somente or listar_stacks():
        st = carregar_stack(sid)
        faltam = [f for f in st.get("requer", []) if not shutil.which(f)]
        if ignorar and sid in ignorar:
            resultados[sid] = {"situacao": "NAO_VERIFICADO", "detalhe": f"não executado nesta máquina: {ignorar[sid]}"}
        elif faltam:
            resultados[sid] = {"situacao": "NAO_VERIFICADO", "detalhe": f"ferramenta ausente: {', '.join(faltam)}"}
        else:
            with tempfile.TemporaryDirectory(prefix=f"stack-{sid}-") as tmp:
                comp = criar_componente(sid, Path(tmp) / "app", "Verificacao")
                r = verificar_componente(sid, comp, logs / sid)
                det = "; ".join(f"{e['nome']}: saída {e['codigo_saida']}" for e in r["execucoes"])
                resultados[sid] = {"situacao": r["situacao"], "detalhe": det, "resumo": r["resumo"]}
        res = resultados[sid]
        tot = res.get("resumo", {})
        linhas.append(f"| {sid} | {st['linguagem']} | {res['situacao']} | {tot.get('testes', '—')} ({tot.get('falhas', 0) + tot.get('erros', 0) if tot else '—'} falhas) | {res['detalhe']} |")
    linhas += ["", "NAO_VERIFICADO = o esqueleto existe, mas não foi executado nesta máquina (motivo na coluna Detalhe). Rode `fabrica.py stacks verificar <stack>` onde a ferramenta estiver disponível.",
               "Logs: `fabrica/stacks/_verificacao/<stack>/`.", ""]
    saida = FAB / "stacks" / "VERIFICACAO.md"
    saida.write_text("\n".join(linhas), encoding="utf-8")
    gravar_json(FAB / "stacks" / "_verificacao" / "resultado.json", {"executado_em": agora(), "resultados": resultados})
    return saida


def verificar_projeto(raiz: Path = RAIZ, instalar: bool = False) -> dict:
    """Roda os testes de todos os componentes declarados no PROJETO.yaml."""
    pj = ler_yaml(raiz / "PROJETO.yaml")
    destino = raiz / "relatorios" / "verificacao"
    saida = {"projeto": pj["projeto"]["id"], "executado_em": agora(), "componentes": {}}
    for c in pj.get("componentes", []):
        saida["componentes"][c["nome"]] = verificar_componente(c["stack"], raiz / c["caminho"], destino / c["nome"], instalar)
    gravar_json(destino / "ULTIMA_VERIFICACAO.json", saida)
    return saida


# --------------------------------------------- modelo de repositório / portfólio

ITENS_MODELO = ["AGENTS.md", "CLAUDE.md", ".claude/settings.json", ".claude/skills", ".codex", "fabrica"]


def exportar_modelo(destino: Path) -> Path:
    """Copia a configuração da fábrica (sem dados de contratos/projetos) para um novo repositório."""
    if destino.exists() and any(destino.iterdir()):
        raise ErroFabrica(f"destino não está vazio: {destino}")
    destino.mkdir(parents=True, exist_ok=True)
    ign = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "_verificacao", "node_modules", "target", "vendor")
    for item in ITENS_MODELO:
        o = RAIZ / item
        if o.is_dir():
            shutil.copytree(o, destino / item, ignore=ign)
        else:
            (destino / item).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(o, destino / item)
    # comunicação começa vazia
    com = destino / "fabrica" / "comunicacao"
    shutil.rmtree(com, ignore_errors=True)
    com.mkdir(parents=True)
    (com / "AGENT_TASKS.json").write_text('{"versao": 1, "tarefas": []}\n', encoding="utf-8")
    (com / "AGENT_MESSAGES.jsonl").write_text("", encoding="utf-8")
    for nome, titulo in (("AGENT_DECISIONS.md", "Decisões registradas"), ("AGENT_HANDOFFS.md", "Transferências de trabalho (handoffs)"),
                         ("AGENT_BLOCKERS.md", "Bloqueios")):
        (com / nome).write_text(f"# {titulo}\n\nRegistro gerado pela CLI. Não edite entradas antigas.\n", encoding="utf-8")
    mr = FAB / "modelos_repositorio"
    for nome, alvo in (("README.md", "README.md"), ("gitignore", ".gitignore"), ("ci.yml", ".github/workflows/ci.yml"),
                       ("PROJETO.yaml", "PROJETO.yaml")):
        (destino / alvo).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(mr / nome, destino / alvo)
    for pasta in ("contratos", "projetos", "relatorios"):
        (destino / pasta).mkdir(exist_ok=True)
        (destino / pasta / ".gitkeep").write_text("", encoding="utf-8")
    try:
        origem = git("rev-parse", "--short", "HEAD").strip()
    except ErroFabrica:
        origem = "sem commit"
    (destino / "fabrica" / "VERSAO_MODELO").write_text(f"exportado em {agora()} de {origem}\n", encoding="utf-8")
    return destino


def novo_repositorio(destino: Path, pid: str, sistema: str, orgao: str = "", contrato: str = "",
                     componentes: list[str] | None = None, git_init: bool = True) -> Path:
    """Cria um repositório completo para UM sistema: configuração da fábrica + esqueletos + PROJETO.yaml."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{1,60}", pid):
        raise ErroFabrica("id do projeto inválido (use letras, números, ponto, hífen; ex.: PMX-001-SGD)")
    exportar_modelo(destino)
    comps = []
    for c in componentes or []:
        nome, _, stack = c.partition("=")
        if not stack:
            raise ErroFabrica(f"componente inválido {c!r}: use nome=stack (ex.: backend=python-fastapi)")
        carregar_stack(stack)
        caminho = f"projetos/{slug(sistema) or slug(pid)}/{nome}"
        criar_componente(stack, destino / caminho, sistema)
        comps.append({"nome": nome, "stack": stack, "caminho": caminho})
    pj = {"projeto": {"id": pid, "sistema": sistema, "orgao": orgao, "contrato": contrato,
                      "repositorio": "", "responsavel_tecnico": "", "criado_em": hoje()},
          "componentes": comps}
    (destino / "PROJETO.yaml").write_text(
        "# Identidade deste repositório (um repositório por sistema). Editado por fabrica.py repositorio novo.\n"
        + yaml.safe_dump(pj, allow_unicode=True, sort_keys=False), encoding="utf-8")
    if contrato:
        subprocess.run([sys.executable, str(destino / "fabrica/ferramentas/fabrica.py"), "contrato", "novo", contrato],
                       check=True, capture_output=True, env={k: v for k, v in os.environ.items() if k != "FABRICA_RAIZ"})
    subprocess.run([sys.executable, str(destino / "fabrica/ferramentas/fabrica.py"), "agentes", "gerar"],
                   check=True, capture_output=True, env={k: v for k, v in os.environ.items() if k != "FABRICA_RAIZ"})
    if git_init:
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=destino, check=True)
    return destino


def repositorios_em_lote(planilha: Path, base: Path) -> list[Path]:
    """Cria um repositório por linha da aba/CSV PROJETOS (até 30 ou mais)."""
    aba = "PROJETOS"
    criados = []
    for r in ler_tabela(planilha, aba):
        comps = [c.strip() for c in (r.get("componentes") or "").split(";") if c.strip()]
        criados.append(novo_repositorio(base / r["id"].lower(), r["id"], r.get("sistema") or r["id"],
                                        r.get("orgao", ""), r.get("contrato", ""), comps))
    return criados


def consolidar_portfolio(repos: list[Path], saida: Path, dia: str | None = None) -> Path:
    """Soma medições e rateios de vários repositórios (portfólio de projetos)."""
    L = ["# Portfólio — consolidado de repositórios", "", f"Gerado em {agora()}.", "",
         "| Repositório | Projeto | Contrato/OS | Previsto | Comprovado | Aceito |", "|---|---|---|---|---|---|"]
    por_prof: dict[str, float] = {}
    tot = {"previsto": 0.0, "comprovado": 0.0, "aceito": 0.0}
    for r in repos:
        pj = (ler_yaml(r / "PROJETO.yaml") or {}).get("projeto", {}) if (r / "PROJETO.yaml").exists() else {}
        for m in sorted(r.glob("contratos/*/medicoes/*.json")):
            med = json.loads(m.read_text(encoding="utf-8"))
            t = med["totais"]
            for k in tot:
                tot[k] += t[k]
            L.append(f"| {r.name} | {pj.get('id', '—')} | {med['contrato']}/{med['os']} | {t['previsto']:g} | {t['comprovado']:g} | {t['aceito']:g} |")
        for rf in r.glob("contratos/*/rateios/*.json"):
            for ln in json.loads(rf.read_text(encoding="utf-8"))["linhas"]:
                if ln.get("ust") is not None:
                    chave = f"{ln['nome']} ({ln['funcao']})"
                    por_prof[chave] = por_prof.get(chave, 0) + ln["ust"]
    L.append(f"| **Total** | | | **{tot['previsto']:g}** | **{tot['comprovado']:g}** | **{tot['aceito']:g}** |")
    L += ["", "## Saldo por projeto", "", "| Repositório | Contrato | Contratado | Aceito | Comprovado | Saldo oficial | Saldo projetado |", "|---|---|---|---|---|---|---|"]
    for r in repos:
        for cdir in sorted(r.glob("contratos/*/contrato.yaml")):
            c = ler_yaml(cdir) or {}
            contratado = numero((c.get("medicao") or {}).get("quantidade_contratada"))
            ac = cp = 0.0
            for m in cdir.parent.glob("medicoes/*.json"):
                tt = json.loads(m.read_text(encoding="utf-8"))["totais"]; ac += tt["aceito"]; cp += tt["comprovado"]
            fmt = lambda x: "—" if x is None else f"{x:g}"  # noqa: E731
            L.append(f"| {r.name} | {cdir.parent.name} | {fmt(contratado)} | {ac:g} | {cp:g} | {fmt(None if contratado is None else contratado - ac)} | {fmt(None if contratado is None else contratado - cp)} |")
    if dia:
        L += ["", f"## Fechamento de {dia} — todos os projetos", "", "| Repositório | Contrato | Quem trabalhou | Commits | Tarefas concluídas | Produção informada |", "|---|---|---|---|---|---|"]
        for r in repos:
            for fj in sorted(r.glob(f"contratos/*/relatorios/fechamentos/{dia}.json")):
                fx = json.loads(fj.read_text(encoding="utf-8"))
                prod = fx.get("producao_informada") or {}
                L.append(f"| {r.name} | {fx['contrato']} | {', '.join(x['nome'] for x in fx['trabalharam']) or 'sem registro'} | {fx['commits']} | {len(fx['tarefas_concluidas'])} | {prod.get('total', '—')} |")
    L += ["", "## Rateio interno somado por profissional (todos os repositórios)", ""]
    L += ["| Profissional | UST atribuída |", "|---|---|", *[f"| {k} | {v:g} |" for k, v in sorted(por_prof.items())]] if por_prof else ["Sem rateios com total informado."]
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text("\n".join(L) + "\n", encoding="utf-8")
    return saida


# ------------------------------------------- edital: exigências, adaptações, confronto

EDITAL_PADRAO = {
    "documentos": {
        "ppj": {"titulo": "Planejamento de Projeto Sustentável (PPJ)", "secoes_extras": []},
        "fechamento": {"titulo": "Fechamento diário"},
        "abertura": {"titulo": "Abertura do dia"},
        "relatorio_diario": {"titulo": "Relatório diário"},
        "relatorio_semanal": {"titulo": "Relatório semanal"},
        "relatorio_mensal": {"titulo": "Relatório mensal"},
    },
    "relatorios_exigidos": ["diario", "semanal", "mensal"],
    "medicao": {"unidade": "UST"},
    "equipe_exigida": [],
    "tecnologias_exigidas": [],
    "certificacoes_empresa_exigidas": [],
    "documentos_exigidos": [],
    "prazos": [],
}
RELATORIOS_SUPORTADOS = {"diario", "semanal", "mensal", "profissional", "fechamento", "abertura", "medicao", "os", "final", "planejamento"}
UNIDADES_SUPORTADAS = {"UST", "PF", "HORA", "ENTREGAVEL"}


def _mesclar(base: dict, extra: dict) -> dict:
    out = dict(base)
    for k, v in (extra or {}).items():
        out[k] = _mesclar(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def edital_cfg(cid: str) -> dict:
    """Exigências e adaptações do edital (EDITAL.yaml do contrato) sobre o padrão da fábrica."""
    p = CONTRATOS / cid / "EDITAL.yaml"
    return _mesclar(EDITAL_PADRAO, (ler_yaml(p) or {}) if p.exists() else {})


def titulo_doc(cid: str, chave: str) -> str:
    return edital_cfg(cid)["documentos"].get(chave, {}).get("titulo", chave)


def normalizar(texto: str) -> str:
    return " " + " ".join(re.findall(r"[a-z0-9+#.]+", unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower())) + " "


def _contem(texto: str, termo: str) -> bool:
    t = normalizar(termo).strip()
    return bool(t) and f" {t} " in normalizar(texto)


def carregar_base(cid: str) -> dict:
    p = CONTRATOS / cid / "BASE.yaml"
    return (ler_yaml(p) or {}) if p.exists() else {}


def confrontar_edital(cid: str) -> dict:
    """Cruza as exigências do edital (EDITAL.yaml) com o documento base (equipe + capacidades) e diz o que atende, o que ajustar e o que falta."""
    d = dir_contrato(cid)
    if not (d / "EDITAL.yaml").exists():
        raise ErroFabrica(f"{cid}: EDITAL.yaml não existe — o Analista de Editais (G02) precisa extrair as exigências primeiro")
    ed = edital_cfg(cid)
    base = carregar_base(cid)
    profs = carregar_profissionais(cid)
    caps = base.get("capacidades") or []
    atende, ajustar, falta = [], [], []
    usados: set[str] = set()
    for req in ed["equipe_exigida"]:
        perfil = req.get("perfil", "")
        qtd = int(req.get("quantidade", 1) or 1)
        termos = req.get("palavras_chave") or [perfil]
        cand = [p for p in profs if p["id"] not in usados and any(_contem(p["funcao"] + " " + p.get("area", ""), t) for t in termos)]
        bons, parciais = [], []
        for p in cand:
            faltas = []
            for c in req.get("certificacoes", []) or []:
                if not _contem(" ".join([p.get("certificacoes", ""), p.get("registro_ou_certificacao", ""), p.get("qualificacao", "")]), c):
                    faltas.append(f"certificação {c}")
            anos = req.get("experiencia_anos")
            if anos and float(re.sub(r"[^\d.]", "", str(p.get("anos_experiencia") or "0")) or 0) < float(anos):
                faltas.append(f"experiência ≥ {anos} anos (informado: {p.get('anos_experiencia') or 'não informado'})")
            if req.get("formacao") and not _contem(p.get("formacao", "") + " " + p.get("qualificacao", ""), req["formacao"]):
                faltas.append(f"formação {req['formacao']}")
            (parciais if faltas else bons).append((p, faltas))
        escolhidos = bons[:qtd]
        for p, _ in escolhidos:
            usados.add(p["id"])
        orig = req.get("origem", "origem não citada")
        if len(escolhidos) >= qtd:
            atende.append(f"Equipe — {perfil} ({qtd}): {', '.join(p['nome'] for p, _ in escolhidos)} [{orig}]")
        else:
            resto = qtd - len(escolhidos)
            for p, f in parciais[:resto]:
                usados.add(p["id"])
                ajustar.append(f"Equipe — {perfil}: {p['nome']} tem a função, mas falta: {', '.join(f)} [{orig}]")
                resto -= 1
            if escolhidos:
                atende.append(f"Equipe — {perfil}: {', '.join(p['nome'] for p, _ in escolhidos)} ({len(escolhidos)} de {qtd}) [{orig}]")
            if resto > 0:
                falta.append(f"Equipe — {perfil}: faltam {resto} profissional(is) "
                             f"(exige {qtd}{'; certificações: ' + ', '.join(req.get('certificacoes') or []) if req.get('certificacoes') else ''}"
                             f"{'; ' + str(req['experiencia_anos']) + ' anos' if req.get('experiencia_anos') else ''}) [{orig}]")
    stacks_txt = " ".join(f"{s} {carregar_stack(s)['linguagem']} {carregar_stack(s).get('framework', '')}" for s in listar_stacks())
    verif = (ler_json(FAB / "stacks" / "_verificacao" / "resultado.json") or {}).get("resultados", {})
    for tec in ed["tecnologias_exigidas"]:
        nome = tec if isinstance(tec, str) else tec.get("nome", "")
        orig = "" if isinstance(tec, str) else f" [{tec.get('origem', '')}]"
        stk = [s for s in listar_stacks() if _contem(f"{s} {carregar_stack(s)['linguagem']} {carregar_stack(s).get('framework', '')}", nome)]
        cap = [c for c in caps if (c.get("tipo") or "").upper() == "TECNOLOGIA" and _contem(c.get("item", "") + " " + c.get("detalhe", ""), nome)]
        compl = [x for x in (ler_yaml(FAB / "stacks" / "complementares" / "tecnologias.yaml") or {}).get("tecnologias", [])
                 if _contem(x["nome"], nome) or _contem(nome, x["nome"])]
        if compl and compl[0]["situacao"] == "verificado" and not stk:
            atende.append(f"Tecnologia — {nome}: usada e testada na fábrica ({compl[0]['evidencia']}){' e experiência declarada' if cap else ''}{orig}")
        elif stk and any(verif.get(s, {}).get("situacao") == "APROVADO" for s in stk):
            atende.append(f"Tecnologia — {nome}: esqueleto verificado ({', '.join(stk)}){' e experiência declarada' if cap else ''}{orig}")
        elif stk or cap:
            ajustar.append(f"Tecnologia — {nome}: {'esqueleto existe mas não verificado (' + ', '.join(stk) + ')' if stk else 'experiência declarada, sem esqueleto na fábrica — criar stack'}{orig}")
        elif _contem(stacks_txt, nome):
            ajustar.append(f"Tecnologia — {nome}: citada parcialmente nas stacks; confirmar versão{orig}")
        else:
            falta.append(f"Tecnologia — {nome}: não há stack nem experiência declarada — criar stack e informar experiência{orig}")
    for cert in ed["certificacoes_empresa_exigidas"]:
        nome = cert if isinstance(cert, str) else cert.get("nome", "")
        ok = [c for c in caps if (c.get("tipo") or "").upper() in ("CERTIFICACAO_EMPRESA", "ATESTADO") and _contem(c.get("item", "") + " " + c.get("detalhe", ""), nome)]
        (atende if ok else falta).append(f"Certificação/atestado da empresa — {nome}: {'informado: ' + ok[0].get('item', '') + (' (prova: ' + ok[0].get('evidencia', '') + ')' if ok[0].get('evidencia') else ' (sem documento anexado)') if ok else 'não consta no documento base'}")
    for r in ed["relatorios_exigidos"]:
        (atende if str(r).lower() in RELATORIOS_SUPORTADOS else ajustar).append(
            f"Relatório {r}: {'gerado pela fábrica' if str(r).lower() in RELATORIOS_SUPORTADOS else 'formato novo — criar modelo (G19)'}")
    un = str(ed["medicao"].get("unidade", "UST")).upper()
    (atende if un in UNIDADES_SUPORTADAS else ajustar).append(f"Medição em {un}: {'suportada' if un in UNIDADES_SUPORTADAS else 'unidade nova — definir regra de medição com base no contrato'}")
    for doc in ed["documentos_exigidos"]:
        nome = doc if isinstance(doc, str) else doc.get("nome", "")
        ajustar.append(f"Documento exigido — {nome}: será gerado com este título; confirmar seções no edital")
    emp = base.get("empresa") or {}
    for campo in ("razao_social", "cnpj", "responsavel_legal", "preposto"):
        if not emp.get(campo):
            falta.append(f"Empresa — {campo.replace('_', ' ')} não informado no documento base")
    if not profs:
        falta.append("Equipe — nenhum profissional cadastrado (basta informar nome e função)")
    r = {"contrato": cid, "gerado_em": agora(), "atende": atende, "ajustar": ajustar, "falta": falta,
         "adaptacoes_aplicadas": {k: v["titulo"] for k, v in ed["documentos"].items()},
         "relatorios_exigidos": ed["relatorios_exigidos"]}
    gravar_json(d / "CONFRONTO_EDITAL.json", r)
    L = [f"# Confronto edital × documento base — {cid}", "", f"Gerado em {r['gerado_em']} (G02 Analista de Editais + G18 Gestor de Profissionais).", "",
         f"Resumo: **{len(atende)} atende · {len(ajustar)} ajustar · {len(falta)} falta**", "",
         "## Já atende", *[f"- ✔ {x}" for x in atende or ["(nada ainda)"]], "",
         "## Precisa ajustar", *[f"- ⚠ {x}" for x in ajustar or ["(nada)"]], "",
         "## Falta (pedir ao responsável)", *[f"- ✘ {x}" for x in falta or ["(nada)"]], "",
         "## Adaptações aplicadas a partir do edital", "",
         *[f"- Documento `{k}` → título **{v}**" for k, v in r["adaptacoes_aplicadas"].items()],
         f"- Relatórios exigidos: {', '.join(map(str, ed['relatorios_exigidos']))}", "",
         "> A comparação é automática por palavras-chave. Itens de equipe e certificações exigem conferência humana dos documentos comprobatórios.", ""]
    (d / "CONFRONTO_EDITAL.md").write_text("\n".join(L), encoding="utf-8")
    exportar_word(d / "CONFRONTO_EDITAL.md", cid, subtitulo="O que atende, o que ajustar e o que falta")
    return r


# ------------------------------------------------------ oportunidades de medição

CATEGORIAS_SERVICO = [
    ("Desenvolvimento de funcionalidades", ["desenvolv", "implement", "codific", "funcionalidade", "manutencao evolutiva"]),
    ("Testes automatizados", ["teste", "qualidade", "homologac"]),
    ("Banco de dados e migrações", ["banco", "dados", "migrac", "modelagem"]),
    ("Infraestrutura e implantação", ["infra", "implant", "deploy", "ambiente", "conteiner", "publicac"]),
    ("Segurança e LGPD", ["seguranc", "vulnerab", "lgpd", "privacidade"]),
    ("Documentação técnica", ["document", "manual"]),
    ("Revisão e inspeção de código", ["revis", "inspec"]),
    ("Interface e protótipos", ["interface", "tela", "prototip", "usabilidade", "acessibilidade"]),
]


def oportunidades_medicao(cid: str, osid: str) -> Path:
    """Lista trabalho REAL comprovado em cada módulo que pode corresponder a itens do catálogo ainda não medidos.

    Não altera a medição: cada linha é uma sugestão para o Medidor (G15) e o responsável confirmarem o enquadramento."""
    o = carregar_os(cid, osid)
    tab = tabela_ust(cid)
    proj = o["projeto"].rstrip("/")
    linhas = []
    for m in o["modulos"]:
        dm = dir_mod(cid, osid, m["id"])
        arquivos = []
        for c in m.get("caminhos", []):
            try:
                arquivos += [a for a in git("ls-files", "--", f"{proj}/{c}").splitlines() if a]
            except ErroFabrica:
                pass
        tj = ler_json(dm / "TESTES.json") or {}
        commits = (ler_json(dm / "COMMITS.json") or {}).get("commits", [])
        rev = (dm / "REVISOES.md").read_text(encoding="utf-8") if (dm / "REVISOES.md").exists() else ""
        caps = list((dm / "SCREENSHOTS").glob("*.png")) if (dm / "SCREENSHOTS").exists() else []
        evid = {
            "Desenvolvimento de funcionalidades": f"{len(commits)} commit(s), {len(arquivos)} arquivo(s)" if commits else "",
            "Testes automatizados": f"{tj.get('resumo', {}).get('testes', 0)} verificações reais ({tj.get('situacao', '')})" if tj.get("resumo", {}).get("testes") else "",
            "Banco de dados e migrações": ", ".join(a.split("/")[-1] for a in arquivos if "migrations/versions" in a and a.endswith(".py"))[:120],
            "Infraestrutura e implantação": ", ".join(sorted({a.split("/")[-1] for a in arquivos if re.search(r"Dockerfile|compose|nginx|infra/", a)}))[:120],
            "Segurança e LGPD": "SEGURANCA.md preenchido" if (dm / "SEGURANCA.md").exists() and "<PREENCHER>" not in (dm / "SEGURANCA.md").read_text(encoding="utf-8") else "",
            "Documentação técnica": ", ".join(a.split("/")[-1] for a in arquivos if a.endswith(".md"))[:120],
            "Revisão e inspeção de código": "revisão registrada em REVISOES.md" if "| 20" in rev else "",
            "Interface e protótipos": f"{len(caps)} captura(s) de tela" if caps else "",
        }
        for cat, termos in CATEGORIAS_SERVICO:
            if not evid.get(cat):
                continue
            itens = [cod for cod, it in tab.items() if not cod.startswith("#") and any(t_ in normalizar(it.get("descricao", "")) for t_ in termos)]
            ja = m.get("item_tabela") in itens
            acao = ("já medido neste módulo" if ja else
                    "verificar enquadramento com o Medidor (G15) e o responsável" if itens else
                    "catálogo não prevê item específico — normalmente incluído no item principal")
            linhas.append({"modulo": m["id"], "categoria": cat, "evidencia": evid[cat], "itens": itens, "acao": acao, "ja_medido": ja})
    sugest = [x for x in linhas if x["itens"] and not x["ja_medido"]]
    L = [f"# Oportunidades de medição — {osid}", "", f"Gerado em {agora()} pelo Medidor de UST (G15).", "",
         "> Lista o trabalho **realmente executado e comprovado** em cada módulo e os itens do catálogo do contrato que podem "
         "corresponder a ele. Nada aqui entra na medição automaticamente: o enquadramento precisa estar previsto no contrato, "
         "não pode haver dupla contagem e depende do aceite do órgão.", "",
         f"Resumo: {len(linhas)} atividade(s) comprovada(s) · {len(sugest)} com item do catálogo a verificar.", "",
         "| Módulo | Atividade comprovada | Evidência | Itens do catálogo | Ação |", "|---|---|---|---|---|"]
    L += [f"| {x['modulo']} | {x['categoria']} | {x['evidencia']} | {', '.join(x['itens']) or '—'} | {x['acao']} |" for x in linhas]
    L += ["", "## Como aumentar a produção de forma legítima", "",
          "- Registrar todo trabalho real no catálogo correto (testes, documentação, migrações, implantação, segurança, quando o contrato prevê).",
          "- Quebrar OS grandes em módulos menores com critério de aceite claro: entregas aceitas mais cedo.",
          "- Reduzir retrabalho e glosas: testes automatizados, revisão antes da entrega, evidências completas.",
          "- Planejar capacidade pela média histórica aceita por profissional (`fabrica.py producao estatisticas`).", ""]
    p = CONTRATOS / cid / "medicoes" / f"{osid}-OPORTUNIDADES.md"
    p.write_text("\n".join(L), encoding="utf-8")
    exportar_word(p, cid, periodo=osid, subtitulo="Trabalho comprovado × catálogo do contrato")
    return p


# ------------------------------------------------------ saldo, fechamento e PPJ

def numero(texto: Any) -> float | None:
    """Primeiro número do texto, aceitando formato brasileiro: '1.500 UST' -> 1500; '10,5' -> 10.5."""
    m = re.search(r"\d[\d.]*(?:,\d+)?", str(texto or ""))
    if not m:
        return None
    v = m.group(0).rstrip(".")
    if "," in v:
        v = v.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", v):
        v = v.replace(".", "")
    return float(v)


def saldo(cid: str) -> dict:
    """Saldo do contrato: contratado − aceito (oficial) e contratado − comprovado (projetado)."""
    d = dir_contrato(cid)
    c = ler_yaml(d / "contrato.yaml") or {}
    contratado = numero((c.get("medicao") or {}).get("quantidade_contratada"))
    tot = {"previsto": 0.0, "comprovado": 0.0, "aceito": 0.0}
    por_os = []
    for m in sorted((d / "medicoes").glob("*.json")):
        med = json.loads(m.read_text(encoding="utf-8"))
        por_os.append({"os": med["os"], **med["totais"], "medido_em": med["medido_em"]})
        for k in tot:
            tot[k] += med["totais"][k]
    r = {"contratado": contratado, **tot, "por_os": por_os,
         "saldo_oficial": None if contratado is None else round(contratado - tot["aceito"], 2),
         "saldo_projetado": None if contratado is None else round(contratado - tot["comprovado"], 2),
         "consumo_aceito_pct": None if not contratado else round(100 * tot["aceito"] / contratado, 1),
         "unidade": edital_cfg(cid)["medicao"].get("unidade", "UST")}
    hist = sorted((d / "relatorios" / "fechamentos").glob("*.json")) if (d / "relatorios" / "fechamentos").exists() else []
    dias = [json.loads(h.read_text(encoding="utf-8")) for h in hist]
    dias_prod = [x for x in dias if (x.get("producao_informada") or {}).get("total")]
    if dias_prod and r["saldo_oficial"] is not None:
        media = sum(x["producao_informada"]["total"] for x in dias_prod) / len(dias_prod)
        r["media_diaria_informada"] = round(media, 2)
        r["dias_para_esgotar"] = round(r["saldo_oficial"] / media, 1) if media else None
    return r


def fechamento(cid: str, ref: str | None = None) -> Path:
    """Fechamento do dia do projeto: nomes, produção, UST do dia, acumulados e saldo."""
    d = dir_contrato(cid)
    dia = ref or hoje()
    date.fromisoformat(dia)
    c = ler_yaml(d / "contrato.yaml") or {}
    profs = {p["id"]: p for p in carregar_profissionais(cid)}
    partic, _ = carregar_participacoes(cid)
    partic = [p for p in partic if p["data"] == dia]
    oss = [ler_yaml(p) for p in sorted((d / "os").glob("*.yaml"))]
    commits = []
    for o in oss:
        try:
            commits += [{**x, "os": o["os"]} for x in _git_periodo(dia, dia, o["projeto"])]
        except ErroFabrica:
            pass
    tarefas = [t for t in carregar_tarefas()["tarefas"] if t["contrato"] == cid]
    concl = [t for t in tarefas if any(h["para"] == "DONE" and h["em"][:10] == dia for h in t["historico"])]
    testes = []
    for o in oss:
        for m in o.get("modulos", []):
            tj = ler_json(dir_mod(cid, o["os"], m["id"]) / "TESTES.json")
            if tj and tj["executado_em"][:10] == dia:
                testes.append((o["os"], m["id"], tj))
    informada = total_informado(cid, "diario", dia)
    rt = rateio(cid, "diario", dia, informada["total"] if informada else None)
    sd = saldo(cid)
    trabalharam = sorted({p["profissional_id"] for p in partic})
    dados = {"contrato": cid, "data": dia, "gerado_em": agora(),
             "trabalharam": [{"id": i, "nome": profs[i]["nome"], "funcao": profs[i]["funcao"]} for i in trabalharam],
             "participacoes": partic, "commits": len(commits), "tarefas_concluidas": [t["id"] for t in concl],
             "testes": sum(t["resumo"]["testes"] for *_, t in testes), "falhas": sum(t["resumo"]["falhas"] + t["resumo"]["erros"] for *_, t in testes),
             "producao_informada": informada, "rateio": rt["linhas"], "saldo": {k: v for k, v in sd.items() if k != "por_os"}}
    pasta = d / "relatorios" / "fechamentos"
    gravar_json(pasta / f"{dia}.json", dados)
    sd = saldo(cid)  # recalcula com o dia gravado (média)
    un = sd["unidade"]
    org = (c.get("contratante") or {}).get("orgao", "")
    L = [f"# {titulo_doc(cid, 'fechamento')} — {dia}", "",
         f"- Projeto/contrato: {cid} · Órgão: {org or 'a cadastrar'} · OS: {', '.join(o['os'] for o in oss) or '—'}",
         f"- Gerado em {dados['gerado_em']} por G19 via `fabrica.py fechamento`", "",
         "## Quem trabalhou hoje", ""]
    L += [f"- {x['nome']} — {x['funcao']}" for x in dados["trabalharam"]] or ["- Sem participação registrada hoje."]
    L += ["", "## Equipe designada", ""]
    L += [f"- {p['nome']} — {p['funcao']}" for p in profs.values()] or ["- Nenhum profissional cadastrado."]
    L += ["", "## Produção do dia", "",
          f"- Commits: {len(commits)}", f"- Tarefas concluídas: {', '.join(dados['tarefas_concluidas']) or 'nenhuma'}",
          f"- Testes executados: {dados['testes']} ({dados['falhas']} falhas)",
          "- Produção informada do dia: " + (f"{informada['total']:g} {un} (base {informada['base'] or 'não informada'}; {informada['documento'] or 'sem documento'})"
                                              if informada else "não informada (RATEIO_TOTAIS.csv, período diario)")]
    medidas = [json.loads(m.read_text(encoding="utf-8")) for m in sorted((d / "medicoes").glob("*.json"))]
    medidas = [m for m in medidas if "totais" in m and str(m.get("medido_em", ""))[:10] == dia]
    for m in medidas:
        tt = m["totais"]
        extra = f" · {tt['horas']:g} h · {brl(tt.get('valor_previsto'))}" if tt.get("horas") is not None else ""
        L.append(f"- Medição registrada hoje ({m['os']}): comprovado {tt['comprovado']:g} {un}{extra} · aceito {tt['aceito']:g}")
    for p in partic:
        L.append(f"  - {profs[p['profissional_id']]['nome']}: {p['tipo']} {p['os']}/{p['modulo']} — {p['descricao']} (prova: {p['evidencia']})")
    L += ["", "## Divisão do dia por profissional", "", *tabela_rateio_md(rt)]
    def f(v):
        return "—" if v is None else f"{v:g}"
    L += ["", "## Saldo do contrato", "",
          f"| Contratado | Previsto (OS) | Comprovado | Aceito | Saldo oficial (contratado − aceito) | Saldo projetado (contratado − comprovado) | Consumo aceito |",
          "|---|---|---|---|---|---|---|",
          f"| {f(sd['contratado'])} {un} | {f(sd['previsto'])} | {f(sd['comprovado'])} | {f(sd['aceito'])} | {f(sd['saldo_oficial'])} | {f(sd['saldo_projetado'])} | {f(sd['consumo_aceito_pct'])}% |"]
    if sd.get("media_diaria_informada"):
        L.append(f"\nMédia diária informada: {sd['media_diaria_informada']:g} {un} → saldo oficial dura cerca de {f(sd.get('dias_para_esgotar'))} dias úteis de produção.")
    if sd["contratado"] is None:
        L.append("\nQuantidade contratada não informada em contrato.yaml (medicao.quantidade_contratada).")
    L += ["", "> Fatos registrados (git, quadro, testes, participações). Produção \"aceita\" só com documento do órgão.", ""]
    (pasta / f"{dia}.md").write_text("\n".join(L), encoding="utf-8")
    exportar_word(pasta / f"{dia}.md", cid, periodo=dia)
    return pasta / f"{dia}.md"


def ppj(cid: str) -> Path:
    """Gera o Planejamento de Projeto Sustentável (título e seções extras adaptáveis pelo EDITAL.yaml)."""
    d = dir_contrato(cid)
    c = ler_yaml(d / "contrato.yaml") or {}
    ed = edital_cfg(cid)
    cfg = ed["documentos"]["ppj"]
    profs = carregar_profissionais(cid)
    sd = saldo(cid)
    oss = [ler_yaml(p) for p in sorted((d / "os").glob("*.yaml"))]
    cont, ctr, tec = c.get("contratante") or {}, c.get("contrato") or {}, c.get("tecnico") or {}
    def v(x):
        return x if x not in (None, "", []) else "**a preencher**"
    un = sd["unidade"]
    L = [f"# {cfg['titulo']} — {cid}", "", f"Gerado em {agora()} pelo Planejador GEC (G04). Itens **a preencher** dependem de informação do contrato ou da equipe.", "",
         "## 1. Identificação", "", f"- Órgão: {v(cont.get('orgao'))}", f"- Contrato: {v(ctr.get('numero'))} · Processo: {v(ctr.get('processo'))} · Edital: {v(ctr.get('edital'))}",
         f"- Objeto: {v(ctr.get('objeto'))}", f"- Vigência: {v(ctr.get('vigencia_inicio'))} a {v(ctr.get('vigencia_fim'))}", "",
         "## 2. Objetivo e escopo", "", f"Executar o objeto contratado com entregas verificáveis por ordem de serviço. OS registradas: {', '.join(o['os'] + ' (' + o.get('titulo', '') + ')' for o in oss) or 'nenhuma'}.", "",
         "## 3. Entregas e módulos", ""]
    for o in oss:
        for m in o.get("modulos", []):
            L.append(f"- {o['os']}/{m['id']} {m['nome']} — área {m.get('area', '—')}, previsto {m.get('ust_previsto', '—')} {un}")
    if not oss:
        L.append("- Nenhuma OS cadastrada.")
    L += ["", "## 4. Equipe", ""]
    L += [f"- {p['nome']} — {p['funcao']}{' (' + p['senioridade'] + ')' if p.get('senioridade') else ''}" for p in profs] or ["- **a preencher** (informe nomes e funções)"]
    L += ["", "## 5. Capacidade, saldo e cronograma", "",
          f"- Contratado: {sd['contratado'] if sd['contratado'] is not None else '**a preencher**'} {un} · Aceito: {sd['aceito']:g} · Comprovado: {sd['comprovado']:g} · Saldo oficial: {sd['saldo_oficial'] if sd['saldo_oficial'] is not None else '—'}",
          f"- Média diária informada: {sd.get('media_diaria_informada', 'sem histórico')} · Projeção de esgotamento: {sd.get('dias_para_esgotar', 'sem histórico')} dias",
          "- Marcos e datas: ver GEC.md, seção 8.", "",
          "## 6. Sustentação (continuidade do serviço)", "",
          "- Manutenção corretiva, adaptativa e evolutiva por OS, com testes de regressão automatizados no CI.",
          "- Monitoramento de saúde (/api/health), backup diário com teste de restauração mensal e plano de recuperação (PLANO_CONTINUIDADE.md).",
          "- Documentação viva (manuais de publicação e operação) e transferência de conhecimento ao fim do contrato (código, migrações, imagens, último backup, histórico de commits).",
          f"- Níveis de serviço do contrato: {v((c.get('medicao') or {}).get('glosas_e_sla'))}", "",
          "## 7. Sustentabilidade", "",
          "Base: Lei 14.133/2021 (desenvolvimento nacional sustentável como princípio e objetivo da contratação) e critérios do edital. Confirmar no texto vigente e no Guia Nacional de Contratações Sustentáveis aplicável.", "",
          "| Dimensão | Prática no projeto | Evidência |", "|---|---|---|",
          "| Ambiental | Processos 100% digitais (sem papel), infraestrutura em contêineres dimensionada à demanda, desligamento de ambientes ociosos | Docker Compose, manuais digitais |",
          "| Ambiental | Reuso de componentes e builds otimizados (menos processamento e tráfego) | build do frontend, cache de estáticos |",
          "| Social | Acessibilidade digital (WCAG/eMAG), proteção de dados (LGPD), capacitação da equipe e do órgão | testes de interface, SEGURANCA_LGPD.md |",
          "| Econômica | Software livre, sem aprisionamento a fornecedor; código e dados entregues ao órgão; medição transparente | pacote de entrega, memória de cálculo |",
          "| Governança | Rastreabilidade (commits, testes, auditoria), revisão humana, relatórios diários | evidências por módulo, fechamentos |", "",
          "## 8. Riscos", "", "- Ver GEC.md (seção 10) e AGENT_BLOCKERS.md.", "",
          "## 9. Indicadores", "", "- Saldo e consumo do contrato (fechamento diário).", "- Taxa de testes aprovados e defeitos reabertos.",
          "- Tempo de atendimento das OS e cumprimento de SLA.", "- Pendências de aceite do órgão.", ""]
    for i, s in enumerate(cfg.get("secoes_extras") or [], start=10):
        nome = s if isinstance(s, str) else s.get("nome", "")
        L += [f"## {i}. {nome} (exigida pelo edital)", "", f"{(s.get('orientacao') if isinstance(s, dict) else '') or '**a preencher** conforme o edital'}", ""]
    L += ["---", "Aprovação humana: **pendente**.", ""]
    p = d / "PPJ.md"
    p.write_text("\n".join(L), encoding="utf-8")
    exportar_word(p, cid, subtitulo="Planejamento, sustentação e sustentabilidade")
    return p


def dias_uteis(ini: date, fim: date) -> int:
    return sum(1 for i in range((fim - ini).days + 1) if (ini + timedelta(days=i)).weekday() < 5)


def carregar_planejamento(cid: str) -> list[dict]:
    p = dir_contrato(cid) / "PLANEJAMENTO.csv"
    if not p.exists():
        raise ErroFabrica(f"{cid}: PLANEJAMENTO.csv não existe (modelo em fabrica/templates/PLANEJAMENTO.csv)")
    return ler_tabela(p)


def planejamento(cid: str, horas_dia: float = 8.0) -> Path:
    """Consolida o planejamento feito pelo usuário: por projeto UST, horas por perfil, valor, prazo e módulos;
    confronta com a capacidade da equipe, o saldo do contrato e o edital."""
    plano = carregar_planejamento(cid)
    profs = carregar_profissionais(cid)
    sd = saldo(cid)
    ed = edital_cfg(cid)
    alertas, linhas = [], []
    for r in plano:
        try:
            calc = calcular_servicos(cid, [{"codigo": r["servico"], "quantidade": r.get("quantidade") or 1}])
        except ErroFabrica as e:
            alertas.append(f"{r.get('projeto')}/{r.get('modulo')}: {e}")
            continue
        ini, fim = date.fromisoformat(r["inicio"]), date.fromisoformat(r["fim"])
        if fim < ini:
            alertas.append(f"{r['projeto']}/{r['modulo']}: fim antes do início")
        linhas.append({**r, **calc, "ini": ini, "fim_d": fim, "dias": dias_uteis(ini, fim)})
    projetos: dict[str, list[dict]] = {}
    for x in linhas:
        projetos.setdefault(x["projeto"], []).append(x)
    unidade = sd["unidade"]
    L = [f"# Plano de projetos — {cid}", "", f"Gerado em {agora()} pelo Planejador GEC (G04) a partir do PLANEJAMENTO.csv preenchido pelo responsável.", "",
         "## Resumo por projeto", "", f"| Projeto | Módulos | {unidade} | Horas | Valor previsto | Início | Fim | Dias úteis |", "|---|---|---|---|---|---|---|---|"]
    tot_q = tot_h = tot_v = 0.0
    for pj, xs in projetos.items():
        q = sum(x["quantidade"] for x in xs); h = sum(x["horas"] for x in xs); v = sum(x["valor"] for x in xs)
        tot_q += q; tot_h += h; tot_v += v
        ini, fim = min(x["ini"] for x in xs), max(x["fim_d"] for x in xs)
        L.append(f"| {pj} | {len(xs)} | {q:g} | {h:g} | {brl(v)} | {ini} | {fim} | {dias_uteis(ini, fim)} |")
    L.append(f"| **Total** | **{len(linhas)}** | **{tot_q:g}** | **{tot_h:g}** | **{brl(tot_v)}** | | | |")
    for pj, xs in projetos.items():
        L += ["", f"## Projeto {pj}", "", f"| Módulo | Nome | Área | Serviço | Qtd | {unidade} | Horas | Início | Fim | Responsável | Prioridade |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        nomes = {p["id"]: p["nome"] for p in profs}
        for x in xs:
            L.append(f"| {x['modulo']} | {x['nome']} | {x.get('area', '')} | {x['servico']} | {x.get('quantidade') or 1} | {x['quantidade']:g} | "
                     f"{x['horas']:g} | {x['ini']} | {x['fim_d']} | {nomes.get(x.get('responsavel', ''), x.get('responsavel') or 'a definir')} | {x.get('prioridade', '')} |")
    # capacidade por perfil
    demanda: dict[str, float] = {}
    for x in linhas:
        for k, v in x["horas_por_perfil"].items():
            demanda[k] = demanda.get(k, 0) + v
    if linhas:
        ini, fim = min(x["ini"] for x in linhas), max(x["fim_d"] for x in linhas)
        du = dias_uteis(ini, fim)
        L += ["", "## Capacidade da equipe por perfil", "", f"Janela {ini} a {fim} ({du} dias úteis, {horas_dia:g} h/dia por pessoa).", "",
              "| Perfil | Horas planejadas | Pessoas no perfil | Capacidade (h) | Ocupação | Situação |", "|---|---|---|---|---|---|"]
        for k, v in sorted(demanda.items()):
            pessoas = [p for p in profs if _contem(p["funcao"] + " " + p.get("area", ""), k.replace("_", " ")) or
                       _contem(k.replace("_", " "), p["funcao"])]
            cap = len(pessoas) * horas_dia * du
            occ = (v / cap * 100) if cap else None
            sit = "SEM PESSOA NO PERFIL" if not pessoas else ("ACIMA DA CAPACIDADE" if v > cap else "ok")
            if sit != "ok":
                alertas.append(f"Perfil {k}: {sit.lower()} ({v:g} h planejadas, {cap:g} h disponíveis)")
            L.append(f"| {k} | {v:g} | {', '.join(p['nome'] for p in pessoas) or '—'} | {cap:g} | {'—' if occ is None else f'{occ:.0f}%'} | {sit} |")
    if sd["saldo_oficial"] is not None and tot_q > sd["saldo_oficial"]:
        alertas.append(f"Planejado ({tot_q:g} {unidade}) maior que o saldo oficial do contrato ({sd['saldo_oficial']:g} {unidade})")
    L += ["", "## Saldo do contrato × plano", "",
          f"- Contratado: {sd['contratado'] if sd['contratado'] is not None else 'não informado'} {unidade} · Aceito: {sd['aceito']:g} · Saldo oficial: {sd['saldo_oficial'] if sd['saldo_oficial'] is not None else '—'}",
          f"- Planejado neste plano: {tot_q:g} {unidade} ({tot_h:g} h, {brl(tot_v)})"]
    if ed.get("prazos"):
        L += ["", "## Prazos do edital", "", *[f"- {p_.get('evento', p_)}: {p_.get('prazo', '')} ({p_.get('origem', '')})" if isinstance(p_, dict) else f"- {p_}" for p_ in ed["prazos"]]]
    L += ["", "## Alertas", "", *([f"- ⚠ {a}" for a in alertas] or ["- Nenhum alerta."]), "",
          "> Planejamento do responsável; quantidades calculadas pela fórmula do contrato sobre o catálogo de serviços. Previsão não é produção nem aceite.", ""]
    p = dir_contrato(cid) / "PLANO_PROJETOS.md"
    p.write_text("\n".join(L), encoding="utf-8")
    gravar_json(dir_contrato(cid) / "PLANO_PROJETOS.json", {"gerado_em": agora(), "alertas": alertas, "totais": {"quantidade": tot_q, "horas": tot_h, "valor": tot_v},
                                                           "linhas": [{k: (str(v) if isinstance(v, date) else v) for k, v in x.items()} for x in linhas]})
    exportar_word(p, cid, subtitulo="Planejamento por projeto: quantidades, horas, prazos e capacidade")
    return p


def gerar_os_do_plano(cid: str, projeto: str, osid: str, caminho_projeto: str) -> Path:
    """Cria o rascunho da OS a partir das linhas do plano de um projeto (sem autorização: precisa de aprovação humana)."""
    xs = [r for r in carregar_planejamento(cid) if r["projeto"] == projeto]
    if not xs:
        raise ErroFabrica(f"projeto {projeto} sem linhas no PLANEJAMENTO.csv")
    destino = dir_contrato(cid) / "os" / f"{osid}.yaml"
    if destino.exists():
        raise ErroFabrica(f"OS já existe: {rel(destino)}")
    os_ = {"os": osid, "contrato": cid, "titulo": f"Projeto {projeto}", "projeto": caminho_projeto,
           "autorizacao": {"autorizado": False, "autorizado_por": "", "data": "", "documento": ""},
           "modulos": [{"id": r["modulo"], "nome": r["nome"], "area": r.get("area", ""),
                        "servicos": [{"codigo": r["servico"], "quantidade": float(r.get("quantidade") or 1)}],
                        "tem_interface": True, "caminhos": [], "testes": []} for r in xs]}
    destino.write_text("# Rascunho gerado do PLANEJAMENTO.csv — complete caminhos/testes e registre a autorização\n"
                       + yaml.safe_dump(os_, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return destino


def abertura(cid: str, ref: str | None = None) -> Path:
    """Abertura do dia: contratado, consumo e saldo; equipe; o que está planejado para hoje; tarefas e bloqueios."""
    d = dir_contrato(cid)
    dia = ref or hoje()
    hoje_d = date.fromisoformat(dia)
    c = ler_yaml(d / "contrato.yaml") or {}
    sd = saldo(cid)
    un = sd["unidade"]
    profs = carregar_profissionais(cid)
    nomes = {p["id"]: p["nome"] for p in profs}
    plano = []
    if (d / "PLANEJAMENTO.csv").exists():
        for r in ler_tabela(d / "PLANEJAMENTO.csv"):
            try:
                if date.fromisoformat(r["inicio"]) <= hoje_d <= date.fromisoformat(r["fim"]):
                    calc = calcular_servicos(cid, [{"codigo": r["servico"], "quantidade": r.get("quantidade") or 1}])
                    du = max(1, dias_uteis(date.fromisoformat(r["inicio"]), date.fromisoformat(r["fim"])))
                    plano.append({**r, **calc, "meta_dia": calc["quantidade"] / du, "horas_dia": calc["horas"] / du})
            except (ErroFabrica, ValueError, KeyError):
                continue
    tarefas = [t for t in carregar_tarefas()["tarefas"] if t["contrato"] == cid]
    andamento = [t for t in tarefas if t["status"] in ("IN_PROGRESS", "IN_REVIEW", "TESTING")]
    prontas = [t for t in tarefas if t["status"] == "READY"]
    bloq = [t for t in tarefas if t["status"] == "BLOCKED"]
    def f(v):
        return "—" if v is None else f"{v:g}"
    L = [f"# {titulo_doc(cid, 'abertura')} — {dia}", "",
         f"- Contrato: {(c.get('contrato') or {}).get('numero') or cid} · Órgão: {(c.get('contratante') or {}).get('orgao') or 'a cadastrar'}",
         f"- Gerado em {agora()} por G01 (Diretor) via `fabrica.py abertura`", "",
         "## Contratado, consumo e saldo", "",
         "| Contratado | Previsto em OS | Comprovado | Aceito | Saldo oficial | Saldo projetado | Consumo aceito |", "|---|---|---|---|---|---|---|",
         f"| {f(sd['contratado'])} {un} | {f(sd['previsto'])} | {f(sd['comprovado'])} | {f(sd['aceito'])} | {f(sd['saldo_oficial'])} | {f(sd['saldo_projetado'])} | {f(sd['consumo_aceito_pct'])}% |", "",
         "## Equipe contratada", "", f"Total: {len(profs)} profissional(is).", ""]
    L += ["| Nome | Cargo | Área | Senioridade |", "|---|---|---|---|", *[f"| {p['nome']} | {p['funcao']} | {p.get('area') or '—'} | {p.get('senioridade') or '—'} |" for p in profs]] if profs else ["Nenhum profissional cadastrado."]
    L += ["", "## Planejado para hoje", ""]
    if plano:
        L += [f"| Projeto | Módulo | Serviço | Responsável | Meta do dia ({un}) | Horas do dia |", "|---|---|---|---|---|---|"]
        L += [f"| {x['projeto']} | {x['modulo']} {x['nome']} | {x['servico']} | {nomes.get(x.get('responsavel', ''), x.get('responsavel') or 'a definir')} | {x['meta_dia']:.2f} | {x['horas_dia']:.1f} |" for x in plano]
        L.append(f"\nMeta total do dia: **{sum(x['meta_dia'] for x in plano):.2f} {un}** ({sum(x['horas_dia'] for x in plano):.1f} h).")
    else:
        L.append("Nada planejado para hoje no PLANEJAMENTO.csv.")
    L += ["", "## Tarefas", "", f"- Em andamento: {len(andamento)} · Prontas para começar: {len(prontas)} · Bloqueadas: {len(bloq)}"]
    L += [f"- {t['id']} [{t['status']}] {t['agente']}: {t['descricao']}" for t in (andamento + prontas)[:15]]
    if bloq:
        L += ["", "## Bloqueios", "", *[f"- {t['id']} {t['agente']}: {t['historico'][-1]['nota']}" for t in bloq]]
    L += ["", "> Abertura = plano do dia. O que foi feito de verdade aparece no relatório diário e no fechamento.", ""]
    pasta = d / "relatorios" / "aberturas"
    pasta.mkdir(parents=True, exist_ok=True)
    p = pasta / f"{dia}.md"
    p.write_text("\n".join(L), encoding="utf-8")
    exportar_word(p, cid, periodo=dia)
    return p


def adicionar_profissional(cid: str, nome: str, funcao: str, area: str = "", senioridade: str = "") -> str:
    """Cadastro mínimo: só nome e função."""
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["nome", "funcao", "area", "senioridade"])
        w.writerow([nome, funcao, area, senioridade])
    r = importar_profissionais(cid, Path(f.name))
    os.unlink(f.name)
    if r["erros"]:
        raise ErroFabrica("; ".join(r["erros"]))
    return next(p["id"] for p in carregar_profissionais(cid) if p["nome"].lower() == nome.strip().lower())


def gerar_pacotes(destino: Path) -> dict[str, Path]:
    """Gera os dois ZIPs: CONFIGURACAO (modelo de repositório) e PREENCHIMENTO (planilha + modelos + guias)."""
    import tempfile
    destino.mkdir(parents=True, exist_ok=True)
    saida = {}
    with tempfile.TemporaryDirectory() as tmp:
        modelo = exportar_modelo(Path(tmp) / "fabrica-modelo")
        z = destino / "CONFIGURACAO_FABRICA.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(modelo.rglob("*")):
                if f.is_file():
                    zf.write(f, Path("fabrica-modelo") / f.relative_to(modelo))
        saida["configuracao"] = z
        pre = Path(tmp) / "PREENCHIMENTO"
        pre.mkdir()
        gerar_planilha(pre / "DOCUMENTO_BASE.xlsx")
        shutil.copytree(FAB / "templates", pre / "modelos_csv_yaml", ignore=shutil.ignore_patterns("evidencias", "PROFISSIONAIS.csv"))
        shutil.copytree(FAB / "templates" / "evidencias", pre / "modelos_evidencia")
        equipe_modelo(pre / "EQUIPE_NOME_CPF_CARGO.docx")
        for doc in ("PREENCHIMENTO_LEIA-ME.md", "O_QUE_ENVIAR.md", "COMO_INICIAR.md", "MEDICAO_UST.md"):
            shutil.copy2(FAB / "docs" / doc, pre / doc)
            exportar_word(pre / doc, subtitulo="Guia da Fábrica de Software Governamental")
        z = destino / "PREENCHIMENTO.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(pre.rglob("*")):
                if f.is_file():
                    zf.write(f, Path("PREENCHIMENTO") / f.relative_to(pre))
        saida["preenchimento"] = z
    return saida


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
    x.add_argument("--data"); x.add_argument("--profissional"); x.add_argument("--total-ust", type=float)

    pf = sp.add_parser("profissionais", help="Equipe real (nome, função, CPF protegido)").add_subparsers(dest="sub", required=True)
    x = pf.add_parser("importar", help="Importa CSV/XLSX (aba PROFISSIONAIS)"); x.add_argument("contrato"); x.add_argument("arquivo")
    x = pf.add_parser("oficial", help="Documento simples Nome/CPF/Cargo em Word (pasta privada)"); x.add_argument("contrato")
    x = pf.add_parser("modelo", help="Modelo Word para preencher Nome/CPF/Cargo"); x.add_argument("destino")
    x = sp.add_parser("rateio", help="Divide o total de UST do período entre a equipe que trabalhou")
    x.add_argument("tipo", choices=["diario", "semanal", "mensal"]); x.add_argument("contrato")
    x.add_argument("--data"); x.add_argument("--total", type=float)
    pl = sp.add_parser("planilha", help="Planilha de preenchimento").add_subparsers(dest="sub", required=True)
    x = pl.add_parser("gerar"); x.add_argument("destino")
    x = pl.add_parser("importar"); x.add_argument("contrato"); x.add_argument("arquivo")
    stx = sp.add_parser("stacks", help="Stacks multi-linguagem").add_subparsers(dest="sub", required=True)
    stx.add_parser("listar")
    x = stx.add_parser("verificar"); x.add_argument("ids", nargs="*")
    x.add_argument("--ignorar", action="append", default=[], help="stack=motivo (registra como NAO_VERIFICADO)")
    x = sp.add_parser("componente", help="Cria esqueleto de uma stack"); x.add_argument("stack"); x.add_argument("destino"); x.add_argument("--nome", default="Sistema")
    x = sp.add_parser("projeto", help="Testa os componentes do PROJETO.yaml"); x.add_argument("sub", choices=["verificar"]); x.add_argument("--instalar", action="store_true")
    x = sp.add_parser("modelo", help="Exporta a configuração da fábrica para um repositório novo"); x.add_argument("sub", choices=["exportar"]); x.add_argument("destino")
    rp = sp.add_parser("repositorio", help="Cria repositório(s) de sistema").add_subparsers(dest="sub", required=True)
    x = rp.add_parser("novo"); x.add_argument("destino"); x.add_argument("--id", required=True); x.add_argument("--sistema", required=True)
    x.add_argument("--orgao", default=""); x.add_argument("--contrato", default=""); x.add_argument("--componente", action="append", default=[])
    x = rp.add_parser("lote", help="Um repositório por linha da aba PROJETOS"); x.add_argument("planilha"); x.add_argument("base")
    x = sp.add_parser("portfolio", help="Consolida vários repositórios"); x.add_argument("repos", nargs="+"); x.add_argument("--saida", default="relatorios/PORTFOLIO.md")
    x.add_argument("--data", help="inclui o fechamento deste dia de todos os projetos")
    x = sp.add_parser("pacotes", help="Gera os ZIPs de configuração e de preenchimento"); x.add_argument("destino")
    ed = sp.add_parser("edital", help="Exigências do edital").add_subparsers(dest="sub", required=True)
    x = ed.add_parser("confrontar", help="Edital × documento base: atende / ajustar / falta"); x.add_argument("contrato")
    x = sp.add_parser("fechamento", help="Fechamento do dia do projeto (nomes, produção, saldo)"); x.add_argument("contrato"); x.add_argument("--data")
    x = sp.add_parser("saldo", help="Saldo do contrato"); x.add_argument("contrato")
    x = sp.add_parser("ppj", help="Planejamento de Projeto Sustentável"); x.add_argument("contrato")
    x = sp.add_parser("oportunidades", help="Trabalho comprovado × catálogo (sugestões de medição)"); x.add_argument("contrato"); x.add_argument("os")
    x = sp.add_parser("word", help="Converte um documento .md da fábrica para Word"); x.add_argument("arquivo"); x.add_argument("--contrato")
    x = sp.add_parser("abertura", help="Abertura do dia (contratado, saldo, equipe, plano do dia)"); x.add_argument("contrato"); x.add_argument("--data")
    pj = sp.add_parser("planejamento", help="Plano por projeto (UST, horas, perfis, prazos, capacidade)").add_subparsers(dest="sub", required=True)
    x = pj.add_parser("consolidar"); x.add_argument("contrato"); x.add_argument("--horas-dia", type=float, default=8.0)
    x = pj.add_parser("gerar-os"); x.add_argument("contrato"); x.add_argument("--projeto", required=True); x.add_argument("--os", required=True)
    x.add_argument("--caminho", required=True, help="pasta do código do projeto, ex.: projetos/gestao-documental")
    x = sp.add_parser("crud", help="Gera CRUD completo (banco, API, testes, tela) a partir de uma especificação")
    x.add_argument("sub", choices=["gerar"]); x.add_argument("especificacao"); x.add_argument("--projeto", required=True)
    x = pf.add_parser("adicionar", help="Cadastro mínimo: nome e função"); x.add_argument("contrato"); x.add_argument("--nome", required=True)
    x.add_argument("--funcao", required=True); x.add_argument("--area", default=""); x.add_argument("--senioridade", default="")

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
            print(rel(relatorio(a.contrato, a.tipo, a.data, a.profissional, a.total_ust)))
        elif a.cmd == "profissionais":
            if a.sub == "importar":
                print(json.dumps(importar_profissionais(a.contrato, Path(a.arquivo)), ensure_ascii=False, indent=2))
            elif a.sub == "modelo":
                print(equipe_modelo(Path(a.destino)))
            elif a.sub == "adicionar":
                print(adicionar_profissional(a.contrato, a.nome, a.funcao, a.area, a.senioridade))
            else:
                print(rel(equipe_oficial(a.contrato)))
        elif a.cmd == "rateio":
            r = rateio(a.contrato, a.tipo, a.data, a.total)
            print("\n".join(tabela_rateio_md(r)))
            exportar_word(CONTRATOS / a.contrato / "rateios" / f"{r['periodo']}-{r['inicio']}.md", a.contrato, periodo=f"{r['inicio']} a {r['fim']}")
        elif a.cmd == "planilha":
            if a.sub == "gerar":
                print(gerar_planilha(Path(a.destino)))
            else:
                print(json.dumps(importar_planilha(a.contrato, Path(a.arquivo)), ensure_ascii=False, indent=2))
        elif a.cmd == "stacks":
            if a.sub == "listar":
                for s in listar_stacks():
                    st = carregar_stack(s); print(f"{s:20} {st['linguagem']:28} {st.get('framework', '')}")
            else:
                ign = dict(i.split("=", 1) for i in a.ignorar)
                print(rel(verificar_stacks(a.ids or None, ign)))
        elif a.cmd == "componente":
            print(criar_componente(a.stack, Path(a.destino), a.nome))
        elif a.cmd == "projeto":
            r = verificar_projeto(RAIZ, a.instalar)
            for nome, c in r["componentes"].items():
                print(f"{nome} ({c['stack']}): {c['situacao']} {c['resumo']}")
        elif a.cmd == "modelo":
            print(exportar_modelo(Path(a.destino)))
        elif a.cmd == "repositorio":
            if a.sub == "novo":
                print(novo_repositorio(Path(a.destino), a.id, a.sistema, a.orgao, a.contrato, a.componente))
            else:
                for r in repositorios_em_lote(Path(a.planilha), Path(a.base)):
                    print(r)
        elif a.cmd == "portfolio":
            print(consolidar_portfolio([Path(r) for r in a.repos], Path(a.saida), a.data))
        elif a.cmd == "edital":
            r = confrontar_edital(a.contrato)
            print(f"atende {len(r['atende'])} · ajustar {len(r['ajustar'])} · falta {len(r['falta'])} → contratos/{a.contrato}/CONFRONTO_EDITAL.md")
        elif a.cmd == "fechamento":
            print(rel(fechamento(a.contrato, a.data)))
        elif a.cmd == "saldo":
            print(json.dumps({k: v for k, v in saldo(a.contrato).items()}, ensure_ascii=False, indent=2))
        elif a.cmd == "ppj":
            print(rel(ppj(a.contrato)))
        elif a.cmd == "oportunidades":
            print(rel(oportunidades_medicao(a.contrato, a.os)))
        elif a.cmd == "abertura":
            print(rel(abertura(a.contrato, a.data)))
        elif a.cmd == "planejamento":
            if a.sub == "consolidar":
                print(rel(planejamento(a.contrato, a.horas_dia)))
            else:
                print(rel(gerar_os_do_plano(a.contrato, a.projeto, a.os, a.caminho)))
        elif a.cmd == "crud":
            sys.path.insert(0, str(Path(__file__).parent))
            from gerador_crud import ErroGerador, gerar_crud
            try:
                arqs = gerar_crud(Path(a.especificacao), RAIZ / a.projeto)
            except ErroGerador as e:
                raise ErroFabrica(str(e))
            for camada, lista in arqs.items():
                print(f"{camada}: {len(lista)} arquivo(s)")
                for x_ in lista:
                    print(f"  {x_}")
        elif a.cmd == "word":
            w = exportar_word(Path(a.arquivo), a.contrato)
            print(w or "Word não gerado (ver aviso)")
        elif a.cmd == "pacotes":
            for k, v in gerar_pacotes(Path(a.destino)).items():
                print(f"{k}: {v}")
        elif a.cmd == "producao":
            print(json.dumps(estatisticas_producao(Path(a.arquivo)), ensure_ascii=False, indent=2))
    except ErroFabrica as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
