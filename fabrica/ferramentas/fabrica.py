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

def _fuso_configurado() -> str:
    p = Path(os.environ.get("FABRICA_RAIZ", Path(__file__).resolve().parents[2])) / "fabrica" / "CONFIGURACAO_FABRICA.yaml"
    try:
        return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("fuso_horario") or "America/Sao_Paulo"
    except (OSError, yaml.YAMLError):
        return "America/Sao_Paulo"


TZ = ZoneInfo(os.environ.get("FABRICA_TZ") or _fuso_configurado())
RAIZ = Path(os.environ.get("FABRICA_RAIZ", Path(__file__).resolve().parents[2]))
FAB = RAIZ / "fabrica"
COM = FAB / "comunicacao"
CONTRATOS = RAIZ / "contratos"
PROJETOS = RAIZ / "projetos"

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
                  subtitulo: str = "", saida: Path | None = None, capa: bool = True, numero_doc: str = "",
                  data_doc: str = "", assinar: bool = False) -> Path | None:
    """Gera a versão Word (.docx) de um documento Markdown da fábrica (capa, cabeçalho, rodapé, tabelas).

    Com empresa.papel_timbrado na configuração, todas as páginas usam o papel timbrado da empresa
    (desligue com FABRICA_TIMBRADO=0). assinar=True acrescenta local, data e assinatura do responsável.
    Desligue o Word com FABRICA_WORD=0. Sem Node/biblioteca docx, avisa e segue (o .md continua valendo)."""
    cfg = configuracao()
    if os.environ.get("FABRICA_WORD", "1") == "0" or cfg.get("gerar_word") is False:
        return None
    meta = {"periodo": periodo, "classificacao": classificacao, "subtitulo": subtitulo, "gerado_em": agora()[:16].replace("T", " "),
            "sem_capa": not capa}
    emp = cfg.get("empresa") or {}
    papel = RAIZ / str(emp.get("papel_timbrado") or "")
    if emp.get("papel_timbrado") and papel.is_file() and os.environ.get("FABRICA_TIMBRADO", "1") != "0":
        meta["timbrado"] = {"imagem": str(papel), "numero": numero_doc, "data": data_doc or hoje(),
                            "empresa": emp.get("razao_social", ""), "local": emp.get("cidade", "")}
        if assinar and emp.get("responsavel_tecnico"):
            meta["timbrado"]["assinatura"] = {"nome": emp["responsavel_tecnico"], "cargo": emp.get("cargo_responsavel", "")}
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
    for equipe, titulo in (("governanca", "Fábrica Governamental (G01–G24)"), ("engenharia", "Engenharia de Software (E01–E20)")):
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
    for equipe, esperado in (("governanca", 24), ("engenharia", 20)):
        n = sum(1 for a in reg["agentes"] if a["equipe"] == equipe)
        if n != esperado:
            problemas.append(f"equipe {equipe} tem {n} agentes (esperado {esperado})")
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


def perfil_casa(funcao: str, perfil: str) -> bool:
    """Cargo × perfil do catálogo tolerando gênero/plural: 'Desenvolvedora Sênior' casa com DESENVOLVEDOR_SENIOR."""
    ignorar = {"de", "da", "do", "das", "dos", "e"}
    tf = [w for w in normalizar(funcao).split() if w not in ignorar]
    tp = [w for w in normalizar(perfil.replace("_", " ")).split() if w not in ignorar]
    raiz = lambda w: w[:-1] if len(w) > 4 and w[-1] in "aos" else w  # noqa: E731
    return bool(tp) and all(any(raiz(a) == raiz(b) or a.startswith(b) or b.startswith(a) for a in tf) for b in tp)


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
        if compl and compl[0]["situacao"] == "verificado":
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
    feriados = {str(x) for x in configuracao()["jornada"].get("feriados") or []}
    return sum(1 for i in range((fim - ini).days + 1)
               if (ini + timedelta(days=i)).weekday() < 5 and (ini + timedelta(days=i)).isoformat() not in feriados)


def carregar_planejamento(cid: str) -> list[dict]:
    p = dir_contrato(cid) / "PLANEJAMENTO.csv"
    if not p.exists():
        raise ErroFabrica(f"{cid}: PLANEJAMENTO.csv não existe (modelo em fabrica/templates/PLANEJAMENTO.csv)")
    return ler_tabela(p)


def planejamento(cid: str, horas_dia: float | None = None) -> Path:
    """Consolida o planejamento feito pelo usuário: por projeto UST, horas por perfil, valor, prazo e módulos;
    confronta com a capacidade da equipe, o saldo do contrato e o edital."""
    horas_dia = horas_dia or float(configuracao()["jornada"]["horas_por_dia"])
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
            pessoas = [p for p in profs if perfil_casa(p["funcao"], k)]
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


# ------------------------------------------------------- configuração central

def configuracao() -> dict:
    p = FAB / "CONFIGURACAO_FABRICA.yaml"
    cfg = (ler_yaml(p) or {}) if p.exists() else {}
    j = cfg.setdefault("jornada", {})
    j.setdefault("horas_por_dia", 8); j.setdefault("aproveitamento", 0.8); j.setdefault("feriados", [])
    cfg.setdefault("producao", {})
    return cfg


def verificar_configuracao() -> list[str]:
    cfg = configuracao()
    avisos = []
    if not (cfg.get("empresa") or {}).get("razao_social"):
        avisos.append("empresa.razao_social vazio")
    j = cfg["jornada"]
    if not (0 < float(j["horas_por_dia"]) <= 12):
        avisos.append("jornada.horas_por_dia fora de 1..12")
    if not (0 < float(j["aproveitamento"]) <= 1):
        avisos.append("jornada.aproveitamento deve estar entre 0 e 1")
    for f in j.get("feriados") or []:
        try:
            date.fromisoformat(str(f))
        except ValueError:
            avisos.append(f"feriado inválido: {f}")
    if not (cfg["producao"].get("produtividade_horas_por_pf")):
        avisos.append("producao.produtividade_horas_por_pf vazio (estimativa de PF/dia indisponível)")
    return avisos


# ------------------------------------------------- capacidade / estimativa de produção

def capacidade(cid: str, dias: int = 21, simular: str = "") -> Path:
    """ESTIMA quanto a equipe produz por dia e por mês (UST, PF, horas, valor). Não é medição."""
    cfg = configuracao()
    j, prod = cfg["jornada"], cfg["producao"]
    hd, aprov = float(j["horas_por_dia"]), float(j["aproveitamento"])
    _, perfis, med = catalogo(cid)
    formula = str(med.get("formula") or "").upper()
    h_pf = numero(med.get("produtividade_horas_por_pf")) or numero(prod.get("produtividade_horas_por_pf"))
    ust_h_padrao = numero(prod.get("ust_por_hora_padrao"))
    pessoas = []
    if simular:  # "DESENVOLVEDOR_PLENO=3,ANALISTA_TESTES=1"
        for par in simular.split(","):
            perfil, _, n = par.partition("=")
            for i in range(int(n or 1)):
                pessoas.append({"nome": f"{perfil.strip()} #{i + 1} (simulado)", "funcao": perfil.strip(), "perfil": perfil.strip()})
    else:
        for p in carregar_profissionais(cid):
            perfil = next((k for k in perfis if perfil_casa(p["funcao"], k)), "")
            pessoas.append({"nome": p["nome"], "funcao": p["funcao"], "perfil": perfil})
    linhas = []
    for x in pessoas:
        h = hd * aprov
        pf_ = perfis.get(x["perfil"], {})
        fator = numero(pf_.get("fator_ust_por_hora"))
        ust = h * fator if (fator is not None and formula in ("HORAS_X_FATOR", "")) else (h * ust_h_padrao if ust_h_padrao else None)
        vh = numero(pf_.get("valor_hora"))
        linhas.append({**x, "horas_dia": h, "ust_dia": ust, "pf_dia": (h / h_pf) if h_pf else None, "valor_dia": h * vh if vh else None})
    def soma(k):
        vs = [l[k] for l in linhas if l[k] is not None]
        return sum(vs) if vs else None
    def f(v, casas=2):
        return "—" if v is None else f"{v:.{casas}f}".replace(".", ",")
    hist = None
    if (dir_contrato(cid) / "PRODUCAO_HISTORICA.csv").exists() and _linhas_reais(dir_contrato(cid) / "PRODUCAO_HISTORICA.csv"):
        hist = estatisticas_producao(dir_contrato(cid) / "PRODUCAO_HISTORICA.csv")
    L = [f"# Capacidade e estimativa de produção — {cid}", "",
         f"Gerado em {agora()} pelo Planejador de Cronograma e Capacidade (G24).", "",
         "> **ESTIMATIVA.** Não é medição nem promessa ao órgão. A produção real sai do trabalho comprovado e do aceite. "
         f"Premissas: {hd:g} h/dia × aproveitamento {aprov:g} = {hd * aprov:g} h produtivas por pessoa; "
         f"UST pelo fator de cada perfil ({'fórmula ' + formula if formula else 'sem fórmula no contrato'}); "
         f"PF por {f(h_pf, 1) + ' h/PF' if h_pf else 'produtividade não informada'}.", "",
         "| Pessoa | Cargo | Perfil do catálogo | Horas produtivas/dia | UST/dia | PF/dia | Valor/dia |", "|---|---|---|---|---|---|---|"]
    for l in linhas:
        L.append(f"| {l['nome']} | {l['funcao']} | {l['perfil'] or 'sem perfil'} | {f(l['horas_dia'], 1)} | {f(l['ust_dia'])} | {f(l['pf_dia'])} | {brl(l['valor_dia']) if l['valor_dia'] else '—'} |")
    if not linhas:
        L.append("| — | nenhuma pessoa cadastrada (use --simular PERFIL=N) | | | | | |")
    L += ["", "## Equipe inteira", "", "| Período | Horas | UST | PF | Valor |", "|---|---|---|---|---|",
          f"| Por dia | {f(soma('horas_dia'), 1)} | {f(soma('ust_dia'))} | {f(soma('pf_dia'))} | {brl(soma('valor_dia')) if soma('valor_dia') else '—'} |",
          f"| Por mês ({dias} dias úteis) | {f((soma('horas_dia') or 0) * dias, 0)} | {f(soma('ust_dia') * dias if soma('ust_dia') is not None else None)} | "
          f"{f(soma('pf_dia') * dias if soma('pf_dia') is not None else None)} | {brl(soma('valor_dia') * dias) if soma('valor_dia') else '—'} |"]
    if hist and hist["linhas"]:
        L += ["", "## Comparação com o histórico real (aceito)", "", "| Profissional | Complexidade | OS | Média UST aceita por OS |", "|---|---|---|---|",
              *[f"| {x['profissional']} | {x['complexidade']} | {x['os_registradas']} | {x['media_ust_por_os']:g} |" for x in hist["linhas"]]]
    L += ["", "## Como melhorar a estimativa", "",
          "- Informe a produtividade (h/PF) do contrato ou do seu histórico em `CONFIGURACAO_FABRICA.yaml` (producao.produtividade_horas_por_pf).",
          "- Cadastre cargos que correspondam aos perfis do catálogo (PERFIS.csv).",
          "- Preencha PRODUCAO_HISTORICA.csv com o que já foi aceito: a comparação mostra o quanto a estimativa está otimista.", ""]
    p = dir_contrato(cid) / "CAPACIDADE.md"
    p.write_text("\n".join(L), encoding="utf-8")
    exportar_word(p, cid, subtitulo="Estimativa de produção por pessoa, dia e mês")
    return p


# --------------------------------------------------------- fluxo (grafo com checkpoints)

NOS_FLUXO = ["autorizacao", "testes", "commits", "auditoria", "medicao", "relatorios", "checklist", "entrega"]


def fluxo(cid: str, osid: str, retomar: bool = True, aprovado_por: str = "", ate: str | None = None) -> dict:
    """Executa a OS do começo ao fim como um grafo de etapas, gravando um checkpoint por etapa.

    Para quando algo falha e PAUSA quando precisa de um humano (autorização ou verificação humana do checklist).
    Inspirado em LangGraph (execução durável + interrupções humanas), sem dependência externa."""
    arq = dir_contrato(cid) / "fluxos" / f"{osid}.json"
    estado = ler_json(arq) if (retomar and arq.exists()) else None
    estado = estado or {"contrato": cid, "os": osid, "criado_em": agora(), "nos": {n: {"status": "PENDENTE"} for n in NOS_FLUXO}}
    estado["situacao"] = "EXECUTANDO"

    def salvar():
        estado["atualizado_em"] = agora()
        gravar_json(arq, estado)

    def rodar(no: str, fn) -> bool:
        info = estado["nos"][no]
        if info.get("status") == "CONCLUIDO":
            return True
        info.update(status="EXECUTANDO", inicio=agora())
        salvar()
        try:
            res = fn()
        except ErroFabrica as e:
            info.update(status="FALHOU", fim=agora(), erro=str(e))
            estado["situacao"] = f"PARADO em {no}: {e}"
            salvar()
            return False
        if isinstance(res, tuple) and res[0] in ("FALHOU", "PAUSA"):
            info.update(status=res[0], fim=agora(), resultado=res[1])
            estado["situacao"] = (f"PAUSADO em {no} (aguardando humano): {res[1]}" if res[0] == "PAUSA" else f"PARADO em {no}: {res[1]}")
            salvar()
            return False
        info.update(status="CONCLUIDO", fim=agora(), resultado=res)
        salvar()
        return True

    def n_autorizacao():
        try:
            exigir_autorizacao(carregar_os(cid, osid))
        except ErroFabrica as e:
            return ("PAUSA", str(e))
        return "autorização registrada"

    def n_testes():
        r = executar_testes(cid, osid)
        ruins = [m for m, x in r.items() if x["situacao"] != "APROVADO"]
        tot = sum(x["resumo"]["testes"] for x in r.values())
        return ("FALHOU", f"módulos com falha: {', '.join(ruins)} — corrigir e rodar com --retomar") if ruins else f"{tot} verificações aprovadas"

    def n_auditoria():
        a = auditar(cid, osid)
        ruins = [m["modulo"] for m in a["modulos"] if m["tecnico"] != "APROVADO"]
        return ("FALHOU", f"auditoria reprovada: {', '.join(ruins)}") if ruins else f"{len(a['modulos'])} módulos aprovados"

    def n_medicao():
        t_ = medir(cid, osid)["totais"]
        return f"previsto {t_['previsto']:g} · comprovado {t_['comprovado']:g} · aceito {t_['aceito']:g}"

    def n_relatorios():
        relatorio(cid, "diario")
        fechamento(cid)
        return "relatório diário e fechamento gerados"

    def n_checklist():
        ck = checklist(cid, osid)
        if ck["situacao_entrega"] == "BLOQUEADA":
            return ("FALHOU", f"críticos reprovados: {', '.join(ck['criticos_reprovados'])}")
        if ck["situacao_entrega"] == "PENDENTE_VERIFICACAO_HUMANA" and not aprovado_por:
            return ("PAUSA", f"{len(ck['criticos_nao_verificados'])} controle(s) crítico(s) aguardam verificação humana — "
                             "verifique e rode de novo com --aprovado-por \"Nome (cargo)\"")
        if aprovado_por:
            estado["aprovacao_humana"] = {"por": aprovado_por, "em": agora()}
        return ck["situacao_entrega"]

    passos = [("autorizacao", n_autorizacao), ("testes", n_testes), ("commits", lambda: f"{sum(coletar_commits(cid, osid).values())} commits"),
              ("auditoria", n_auditoria), ("medicao", n_medicao), ("relatorios", n_relatorios), ("checklist", n_checklist),
              ("entrega", lambda: rel(preparar_entrega(cid, osid)))]
    for no, fn in passos:
        if estado["nos"][no].get("status") in ("PAUSA", "FALHOU"):
            estado["nos"][no]["status"] = "PENDENTE"  # nova tentativa
        if not rodar(no, fn):
            return estado
        if ate and no == ate:
            estado["situacao"] = f"PARADO a pedido após {no}"
            salvar()
            return estado
    estado["situacao"] = "CONCLUIDO"
    salvar()
    return estado


# ------------------------------------------------------------------ GEC completo

def gec(cid: str) -> Path:
    """Plano de Gestão da Execução Contratual completo, montado dos dados do contrato, do edital e do plano.

    Separa ESTIMATIVA (plano, cronograma, custos) de EXECUÇÃO REAL (comprovado/aceito) e cita a origem de cada exigência."""
    d = dir_contrato(cid)
    c = ler_yaml(d / "contrato.yaml") or {}
    ed = edital_cfg(cid)
    edraw = (ler_yaml(d / "EDITAL.yaml") or {}) if (d / "EDITAL.yaml").exists() else {}
    cont, ctr, med, tec = c.get("contratante") or {}, c.get("contrato") or {}, c.get("medicao") or {}, c.get("tecnico") or {}
    profs = carregar_profissionais(cid)
    cat, perfis, _ = catalogo(cid)
    sd = saldo(cid)
    un = sd["unidade"]
    reg = carregar_registro()
    def v(x, padrao="**a preencher**"):
        return padrao if x in (None, "", []) else x
    def f(x):
        return "—" if x is None else f"{x:g}".replace(".", ",")
    L = [f"# Plano de Gestão da Execução Contratual (GEC) — {cid}", "",
         f"Gerado em {agora()} pelo Planejador GEC (G04) com apoio de G02, G21, G22, G23 e G24. Itens **a preencher** dependem do edital ou do responsável.", "",
         "> **Legenda:** ESTIMATIVA = planejado/calculado antes da execução · REAL = comprovado (auditado) ou aceito pelo órgão. "
         "Cada exigência indica a origem (documento, cláusula, página).", ""]
    L += ["## 1. Identificação do contrato", "", "| Campo | Valor |", "|---|---|",
          f"| Órgão contratante | {v(cont.get('orgao'))} |", f"| Esfera | {v(cont.get('esfera'))} |",
          f"| Contrato / processo / edital | {v(ctr.get('numero'))} / {v(ctr.get('processo'))} / {v(ctr.get('edital'))} |",
          f"| Regime jurídico | {v(ctr.get('regime_juridico'))} |", f"| Vigência | {v(ctr.get('vigencia_inicio'))} a {v(ctr.get('vigencia_fim'))} |",
          f"| Valor global | {v(ctr.get('valor_global'))} |", f"| Gestor / fiscal do contrato | {v(cont.get('gestor_contrato'))} / {v(cont.get('fiscal_tecnico'))} |",
          f"| Preposto da contratada | {v((c.get('equipe') or {}).get('preposto'))} |", ""]
    L += ["## 2. Objeto e escopo", "", f"**Objeto:** {v(ctr.get('objeto'))}", "",
          f"Tecnologias obrigatórias: {', '.join(tec.get('tecnologias_obrigatorias') or []) or 'a preencher'} · Banco: {v(tec.get('banco_de_dados'))} · "
          f"Infraestrutura: {v(tec.get('infraestrutura'))}", "", "Matriz de rastreabilidade completa: `MATRIZ_RASTREABILIDADE.md`.", ""]
    L += ["## 3. Serviços contratados — explicação técnica", ""]
    servs = edraw.get("servicos") or []
    if servs:
        L += ["| Código | Serviço | Explicação técnica | Unidade | Origem |", "|---|---|---|---|---|"]
        L += [f"| {s_.get('codigo', '')} | {s_.get('nome', '')} | {s_.get('explicacao_tecnica', 'a preencher')} | {s_.get('unidade', un)} | {s_.get('origem', 'a citar')} |" for s_ in servs]
    else:
        L.append("A preencher pelo Analista de Editais (G02) em `EDITAL.yaml` → `servicos` (código, nome, explicação técnica, unidade, origem).")
    if cat:
        L += ["", "**Catálogo de serviços × perfis (horas por execução):**", "", "| Serviço | Perfil | Horas | Origem |", "|---|---|---|---|"]
        L += [f"| {cod} — {ln['servico']} | {ln['perfil']} | {ln['horas']} | {ln.get('referencia', '')} |" for cod, lns in cat.items() for ln in lns]
    L += ["", "## 4. Equipe exigida × equipe designada", ""]
    exig = ed.get("equipe_exigida") or []
    if exig:
        L += ["| Perfil exigido | Qtd | Requisitos | Origem |", "|---|---|---|---|"]
        L += [f"| {e.get('perfil', '')} | {e.get('quantidade', 1)} | {', '.join(filter(None, [', '.join(e.get('certificacoes') or []), (str(e['experiencia_anos']) + ' anos') if e.get('experiencia_anos') else '', e.get('formacao', '')])) or '—'} | {e.get('origem', 'a citar')} |" for e in exig]
    else:
        L.append("Perfis exigidos: a preencher (EDITAL.yaml → equipe_exigida).")
    L += ["", "**Designados:**", ""]
    L += [f"- {p['nome']} — {p['funcao']}{' (' + p['senioridade'] + ')' if p.get('senioridade') else ''}" for p in profs] or \
         ["- Nomes a informar no final (a fábrica trabalha com os perfis; os nomes entram no cadastro da equipe antes da entrega)."]
    if (d / "CONFRONTO_EDITAL.md").exists():
        L.append("\nConfronto completo edital × documento base: `CONFRONTO_EDITAL.md`.")
    L += ["", "## 5. Organização: agentes de IA e responsabilidade humana", "",
          "| Etapa | Agentes de IA | Responsável humano (aprova) |", "|---|---|---|",
          "| Leitura do edital, habilitação, SLAs | G02, G21, G23 | Gestor do contrato |",
          "| Planejamento, cronograma, custos | G04, G24, G22 | Gerente de projeto |",
          "| Arquitetura e desenvolvimento | G05, G06–G09, E01–E13 | Responsável técnico |",
          "| Testes, revisão, segurança | G12, G13, G10, E16–E18 | Responsável técnico |",
          "| Evidências, medição, relatórios | G17, G15, G16, G19 | Gerente de projeto / preposto |",
          "| Homologação e entrega | G20, G11 | Fiscal do órgão (aceite) |",
          f"\nTotal: {len(reg['agentes'])} agentes de IA (lista em `fabrica/docs/EQUIPE_AGENTES.md`)."]
    plano_j = ler_json(d / "PLANO_PROJETOS.json") if (d / "PLANO_PROJETOS.json").exists() else None
    if not plano_j and (d / "PLANEJAMENTO.csv").exists() and _linhas_reais(d / "PLANEJAMENTO.csv"):
        try:
            planejamento(cid)
            plano_j = ler_json(d / "PLANO_PROJETOS.json")
        except ErroFabrica:
            plano_j = None
    L += ["", "## 6. Planejamento por projeto (ESTIMATIVA)", ""]
    linhas = (plano_j or {}).get("linhas", [])
    if linhas:
        por: dict[str, list] = {}
        for x in linhas:
            por.setdefault(x["projeto"], []).append(x)
        L += [f"| Projeto | Módulos | {un} | Horas | Valor | Início | Fim |", "|---|---|---|---|---|---|---|"]
        for pj, xs in por.items():
            L.append(f"| {pj} | {len(xs)} | {f(sum(x['quantidade'] for x in xs))} | {f(sum(x['horas'] for x in xs))} | {brl(sum(x['valor'] for x in xs))} | "
                     f"{min(x['ini'] for x in xs)} | {max(x['fim_d'] for x in xs)} |")
        L += ["", f"| Projeto | Módulo | Serviço | {un} | Horas | Início | Fim | Responsável |", "|---|---|---|---|---|---|---|---|"]
        L += [f"| {x['projeto']} | {x['modulo']} {x['nome']} | {x['servico']} | {f(x['quantidade'])} | {f(x['horas'])} | {x['ini']} | {x['fim_d']} | {x.get('responsavel') or 'a definir'} |" for x in linhas]
        # cronograma diário e mensal
        dia_a_dia: dict[str, dict] = {}
        feriados = {str(x) for x in configuracao()["jornada"].get("feriados") or []}
        for x in linhas:
            ini, fim = date.fromisoformat(x["ini"]), date.fromisoformat(x["fim_d"])
            uteis = [ini + timedelta(days=i) for i in range((fim - ini).days + 1)
                     if (ini + timedelta(days=i)).weekday() < 5 and (ini + timedelta(days=i)).isoformat() not in feriados]
            for dd in uteis:
                k = dd.isoformat()
                e_ = dia_a_dia.setdefault(k, {"mods": [], "q": 0.0, "h": 0.0, "v": 0.0})
                e_["mods"].append(x["modulo"]); e_["q"] += x["quantidade"] / len(uteis); e_["h"] += x["horas"] / len(uteis); e_["v"] += x["valor"] / len(uteis)
        dias_ord = sorted(dia_a_dia)
        L += ["", "## 7. Cronograma diário (ESTIMATIVA)", "", f"| Dia | Módulos em execução | Meta ({un}) | Horas | Valor |", "|---|---|---|---|---|"]
        for k in dias_ord[:62]:
            e_ = dia_a_dia[k]
            L.append(f"| {k} | {', '.join(e_['mods'])} | {e_['q']:.2f} | {e_['h']:.1f} | {brl(e_['v'])} |")
        if len(dias_ord) > 62:
            L.append(f"| … | mais {len(dias_ord) - 62} dia(s) úteis | | | |")
        meses: dict[str, dict] = {}
        for k, e_ in dia_a_dia.items():
            m_ = meses.setdefault(k[:7], {"q": 0.0, "h": 0.0, "v": 0.0, "dias": 0})
            m_["q"] += e_["q"]; m_["h"] += e_["h"]; m_["v"] += e_["v"]; m_["dias"] += 1
        L += ["", "## 8. Cronograma mensal e mensalidades (ESTIMATIVA)", "", f"| Mês | Dias úteis com execução | {un} | Horas | Mensalidade estimada |", "|---|---|---|---|---|"]
        L += [f"| {k} | {m_['dias']} | {m_['q']:.2f} | {m_['h']:.1f} | {brl(m_['v'])} |" for k, m_ in sorted(meses.items())]
        L.append(f"\nPagamento conforme o contrato: {v((edraw.get('pagamento') or {}).get('regra'), 'a preencher (EDITAL.yaml → pagamento.regra, ex.: mensal após aceite)')}.")
    else:
        L.append("Sem PLANEJAMENTO.csv preenchido: o plano por projeto, o cronograma diário/mensal e as mensalidades aparecem aqui quando o responsável preencher o plano.")
    L += ["", "## 9. Medição e cálculos", "",
          f"- Modalidade: {v(med.get('modalidade'))} · Metodologia: {v(med.get('metodologia'))} · Fórmula: {v(med.get('formula'))}",
          f"- Quantidade contratada: {v(med.get('quantidade_contratada'))} · Valor unitário: {v(med.get('valor_unitario'))}",
          f"- Medição parcial: {v(med.get('regra_medicao_parcial'))}", ""]
    if perfis:
        L += ["| Perfil | Valor/hora | Fator UST/hora | Origem |", "|---|---|---|---|"]
        L += [f"| {k} | {brl(numero(p_.get('valor_hora')))} | {p_.get('fator_ust_por_hora', '—')} | {p_.get('referencia', '')} |" for k, p_ in perfis.items()]
    hpf = numero(med.get("produtividade_horas_por_pf")) or numero(configuracao()["producao"].get("produtividade_horas_por_pf"))
    L += ["", f"- Pontos de função: {'produtividade de ' + f(hpf) + ' h/PF (ESTIMATIVA de esforço)' if hpf else 'contagem pela metodologia do contrato (G16); produtividade h/PF não informada'}.",
          "- Regras: previsto = OS; comprovado = auditoria aprovada; aceito = documento do órgão. UST/PF/horas só se convertem pela fórmula do contrato.", ""]
    L += ["## 10. Custos estimados por perfil (ESTIMATIVA)", ""]
    if linhas:
        hp: dict[str, float] = {}
        for x in linhas:
            for k, h in x["horas_por_perfil"].items():
                hp[k] = hp.get(k, 0) + h
        L += ["| Perfil | Horas planejadas | Valor/hora | Custo estimado |", "|---|---|---|---|"]
        tot = 0.0
        for k, h in sorted(hp.items()):
            vh = numero((perfis.get(k) or {}).get("valor_hora"))
            tot += h * (vh or 0)
            L.append(f"| {k} | {f(h)} | {brl(vh)} | {brl(h * vh) if vh else '—'} |")
        L.append(f"| **Total** | **{f(sum(hp.values()))}** | | **{brl(tot)}** |")
    else:
        L.append("Depende do planejamento.")
    L += ["", "## 11. Documentos de habilitação", ""]
    hab = edraw.get("habilitacao") or []
    if hab:
        L += ["| Grupo | Documento | Exigência | Origem | Situação |", "|---|---|---|---|---|"]
        L += [f"| {h.get('grupo', '')} | {h.get('documento', '')} | {h.get('exigencia', '')} | {h.get('origem', 'a citar')} | {h.get('situacao', 'a verificar')} |" for h in hab]
    else:
        L.append("A preencher pelo Analista de Habilitação (G21) em `EDITAL.yaml` → `habilitacao` (jurídica, fiscal/trabalhista, técnica, econômico-financeira).")
    L += ["", "## 12. Níveis de serviço (SLA) e glosas", ""]
    slas = edraw.get("slas") or []
    if slas:
        L += ["| Indicador | Meta | Como medir | Glosa | Origem |", "|---|---|---|---|---|"]
        L += [f"| {s_.get('indicador', '')} | {s_.get('meta', '')} | {s_.get('medicao', '')} | {s_.get('glosa', '')} | {s_.get('origem', 'a citar')} |" for s_ in slas]
    else:
        L.append(f"A preencher pelo Analista de SLA (G23) em `EDITAL.yaml` → `slas`. Contrato: {v(med.get('glosas_e_sla'))}.")
    L += ["", "## 13. Relatórios e evidências", "",
          f"- Relatórios exigidos: {', '.join(map(str, ed.get('relatorios_exigidos') or [])) or 'a preencher'} (títulos adaptados ao edital).",
          "- Todo dia: abertura, relatório diário e fechamento (Word).",
          "- Por módulo: 15 evidências obrigatórias (escopo, requisitos, arquitetura, código alterado, commits, testes, logs, segurança, preview, capturas, revisões, responsáveis, medição, implantação, aceite).",
          "- Checklist de 100 controles antes de cada entrega.", ""]
    L += ["## 14. Riscos", ""]
    alertas = (plano_j or {}).get("alertas", [])
    bloq = [t for t in carregar_tarefas()["tarefas"] if t["contrato"] == cid and t["status"] == "BLOCKED"]
    L += [f"- ⚠ {a}" for a in alertas] + [f"- ⛔ {t['id']}: {t['historico'][-1]['nota']}" for t in bloq] or ["- Nenhum risco registrado."]
    L += ["", "## 15. Comunicação e controle de mudanças", "",
          "- Canal com o órgão: gestor/fiscal do contrato. Relatórios diários e mensais em Word.",
          "- Mudança de escopo = registro de decisão + nova linha no planejamento + aprovação humana + aditivo quando o contrato exigir.", ""]
    L += ["## 16. ESTIMATIVA × EXECUÇÃO REAL", "",
          f"| Medida | Planejado (ESTIMATIVA) | Comprovado (REAL) | Aceito (REAL) |", "|---|---|---|---|",
          f"| {un} | {f((plano_j or {}).get('totais', {}).get('quantidade'))} | {f(sd['comprovado'])} | {f(sd['aceito'])} |",
          f"| Saldo do contrato | — | {f(sd['saldo_projetado'])} (projetado) | {f(sd['saldo_oficial'])} (oficial) |", ""]
    pp = proximo_passo(cid)
    falta = [e["etapa"] for e in pp["etapas"] if not e["ok"]]
    L += ["## 17. Pendências para completar este GEC", "", *([f"- {x}" for x in falta] or ["- Nenhuma."]), "",
          "---", "Aprovação humana do GEC: **pendente** (responsável técnico e gestor do contrato).", ""]
    p = d / "GEC.md"
    p.write_text("\n".join(L), encoding="utf-8")
    exportar_word(p, cid, subtitulo="Plano de Gestão da Execução Contratual")
    return p


# ------------------------------------------------------------- próximo passo

def _linhas_reais(p: Path) -> int:
    return len(ler_tabela(p)) if p.exists() else 0


def proximo_passo(cid: str | None = None, dia: str | None = None) -> dict:
    """Diagnóstico do começo ao fim: o que já está pronto, o que falta e a próxima ação (frase para o chat + comando)."""
    dia = dia or hoje()
    etapas: list[dict] = []

    def etapa(n: str, ok: bool, fazer: str, comando: str = "", detalhe: str = "") -> None:
        etapas.append({"etapa": n, "ok": bool(ok), "fazer": fazer, "comando": comando, "detalhe": detalhe})

    agentes_ok = not verificar_agentes()
    word_ok = subprocess.run(["node", "-e", "require('docx')"], capture_output=True, cwd=FAB / "ferramentas").returncode == 0 \
        if shutil.which("node") else False
    etapa("Fábrica configurada (44 agentes, comandos, regras)", agentes_ok, "Diga: INICIAR FÁBRICA", "fabrica.py agentes gerar && fabrica.py iniciar")
    etapa("Gerador de Word disponível", word_ok, "Rode uma vez: npm install --prefix fabrica/ferramentas", "npm install --prefix fabrica/ferramentas")
    contratos = sorted(p.name for p in CONTRATOS.iterdir() if p.is_dir() and (p / "contrato.yaml").exists()) if CONTRATOS.exists() else []
    if not cid:
        reais = [c for c in contratos if not c.startswith("TESTE-")]
        cid = reais[0] if len(reais) == 1 else None
    if not cid:
        etapa("Contrato criado", False, "Envie o edital/TR/contrato (PDF) e diga: NOVO CONTRATO <ID> (ex.: CT-12-2026)",
              "fabrica.py contrato novo <ID>", f"contratos existentes: {', '.join(contratos) or 'nenhum'}")
        return {"contrato": None, "etapas": etapas, "proximo": next(e for e in etapas if not e["ok"])}
    d = dir_contrato(cid)
    docs = [x for x in (d / "documentos").glob("*") if x.suffix.lower() in (".pdf", ".docx", ".doc", ".odt")] if (d / "documentos").exists() else []
    etapa("Documentos do edital recebidos", docs or cid.startswith("TESTE-"), "Anexe edital, TR, contrato e OS na conversa (vão para contratos/<ID>/documentos)",
          detalhe=f"{len(docs)} documento(s)")
    ed = ler_yaml(d / "EDITAL.yaml") if (d / "EDITAL.yaml").exists() else {}
    ed_ok = bool(ed and (ed.get("equipe_exigida") or ed.get("tecnologias_exigidas") or ed.get("relatorios_exigidos")))
    etapa("Exigências do edital extraídas (EDITAL.yaml)", ed_ok, f"Diga: ANALISAR EDITAL {cid}", "skill analisar-edital → EDITAL.yaml")
    falt = campos_faltantes(cid)
    etapa("Formulário do contrato completo", len(falt) <= 3, f"Diga: O QUE FALTA NO CONTRATO {cid} — e responda às perguntas",
          f"fabrica.py contrato faltantes {cid}", f"{len(falt)} campo(s) faltando")
    profs = carregar_profissionais(cid)
    etapa("Equipe cadastrada (nome e cargo)", profs, f"Preencha o Word EQUIPE_NOME_CPF_CARGO e diga: IMPORTAR EQUIPE {cid}",
          f"fabrica.py profissionais importar {cid} EQUIPE.docx", f"{len(profs)} profissional(is)")
    base = carregar_base(cid)
    etapa("Documento base (empresa e capacidades)", (base.get("empresa") or {}).get("razao_social"),
          f"Preencha DOCUMENTO_BASE.xlsx e diga: IMPORTAR DOCUMENTO BASE {cid}", f"fabrica.py planilha importar {cid} DOCUMENTO_BASE.xlsx")
    etapa("Confronto edital × documento base", (d / "CONFRONTO_EDITAL.json").exists(), f"Diga: CONFRONTAR EDITAL {cid}", f"fabrica.py edital confrontar {cid}")
    med = (ler_yaml(d / "contrato.yaml") or {}).get("medicao") or {}
    medicao_ok = (str(med.get("formula") or "").upper() in FORMULAS and _linhas_reais(d / "CATALOGO_SERVICOS.csv")) or _linhas_reais(d / "TABELA_UST.csv")
    etapa("Regra de medição do contrato (tabela UST ou perfis + catálogo + fórmula)", medicao_ok,
          f"Copie a tabela do TR para TABELA_UST.csv, ou PERFIS + CATALOGO_SERVICOS + medicao.formula; diga: CONFIGURAR MEDIÇÃO {cid}")
    plano = _linhas_reais(d / "PLANEJAMENTO.csv")
    etapa("Seu planejamento preenchido (aba PLANEJAMENTO)", plano, "Preencha a aba PLANEJAMENTO (projeto, módulo, serviço, datas, responsável)",
          detalhe=f"{plano} linha(s)")
    etapa("Plano por projeto consolidado", (d / "PLANO_PROJETOS.md").exists(), f"Diga: PLANEJAMENTO {cid}", f"fabrica.py planejamento consolidar {cid}")
    oss = sorted((d / "os").glob("*.yaml"))
    etapa("Ordem de serviço criada", oss, f"Diga: GERAR OS DO PROJETO <projeto> {cid}", f"fabrica.py planejamento gerar-os {cid} --projeto <P> --os <OS> --caminho projetos/<sistema>")
    autorizadas = [o for o in oss if ((ler_yaml(o) or {}).get("autorizacao") or {}).get("autorizado") is True]
    etapa("OS autorizada por quem pode autorizar", autorizadas, "Informe quem autorizou, a data e o documento (OS assinada) — sem isso nada é executado",
          detalhe=f"{len(autorizadas)} de {len(oss)} OS autorizadas")
    for o in autorizadas:
        oy = ler_yaml(o)
        mods = oy.get("modulos", [])
        tj = [ler_json(dir_mod(cid, oy["os"], m["id"]) / "TESTES.json") or {} for m in mods]
        etapa(f"{oy['os']}: código feito e testado", mods and all(x.get("situacao") == "APROVADO" for x in tj),
              f"Diga: EXECUTAR OS {oy['os']}", f"fabrica.py testes executar {cid} {oy['os']}",
              f"{sum(1 for x in tj if x.get('situacao') == 'APROVADO')} de {len(mods)} módulos aprovados")
        etapa(f"{oy['os']}: evidências auditadas e medição", (d / "medicoes" / f"{oy['os']}.json").exists(),
              f"Diga: AUDITAR EVIDÊNCIAS e MEDIR PRODUÇÃO {oy['os']}", f"fabrica.py auditar {cid} {oy['os']} && fabrica.py medir {cid} {oy['os']}")
    rel_ = d / "relatorios"
    etapa(f"Abertura do dia {dia}", (rel_ / "aberturas" / f"{dia}.md").exists(), f"Diga: ABERTURA DO DIA {cid}", f"fabrica.py abertura {cid}")
    etapa(f"Relatório diário {dia}", (rel_ / "diarios" / f"{dia}.md").exists(), f"Diga: RELATÓRIO DIÁRIO {cid}", f"fabrica.py relatorio diario {cid}")
    etapa(f"Fechamento do dia {dia}", (rel_ / "fechamentos" / f"{dia}.md").exists(), f"Diga: FECHAMENTO DO DIA {cid}", f"fabrica.py fechamento {cid}")
    pend = next((e for e in etapas if not e["ok"]), None)
    return {"contrato": cid, "dia": dia, "etapas": etapas, "proximo": pend}


def texto_proximo_passo(r: dict) -> str:
    L = [f"# Próximo passo — {r['contrato'] or 'sem contrato'}", ""]
    if r["proximo"]:
        L += [f"**Agora:** {r['proximo']['fazer']}", ""]
    else:
        L += ["**Tudo em dia.** Continue a rotina: abertura → execução → relatório diário → fechamento.", ""]
    L += ["| | Etapa | Situação | O que fazer |", "|---|---|---|---|"]
    for i, e in enumerate(r["etapas"], start=1):
        L.append(f"| {i} | {e['etapa']} | {'✔ pronto' if e['ok'] else '✘ falta'}{' — ' + e['detalhe'] if e['detalhe'] else ''} | {'' if e['ok'] else e['fazer']} |")
    return "\n".join(L) + "\n"


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
        shutil.copy2(FAB / "CONFIGURACAO_FABRICA.yaml", pre / "CONFIGURACAO_FABRICA.yaml")
        for doc in ("TREINAMENTO.md", "PROMPT_INICIAL.md", "PREENCHIMENTO_LEIA-ME.md", "O_QUE_ENVIAR.md", "COMO_INICIAR.md", "MEDICAO_UST.md"):
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
    ok("44 agentes (24 G + 20 E) gerados e válidos", not prob, "; ".join(prob[:3]))
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


# ------------------------------------------------------- relatório técnico (para o órgão)

EXT_TEXTO = {".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript (React)", ".js": "JavaScript", ".cjs": "JavaScript",
             ".mjs": "JavaScript", ".sql": "SQL", ".css": "CSS", ".html": "HTML", ".yml": "YAML", ".yaml": "YAML",
             ".json": "JSON", ".md": "Markdown", ".sh": "Shell", ".conf": "Configuração", ".ini": "Configuração",
             ".toml": "Configuração", ".txt": "Texto"}
IGNORAR_CODIGO = ("package-lock.json", ".sha256", ".dump", ".tar.gz", ".png", ".jpg", ".pdf", ".zip")


def camada_arquivo(f: str) -> str:
    """Classifica um arquivo do sistema na camada que ele implementa."""
    fl = f.lower()
    nome = fl.rsplit("/", 1)[-1]
    if "/tests/" in fl or nome.startswith("test_") or ".test." in nome or "/e2e/" in fl or nome == "conftest.py":
        return "Testes automatizados"
    if "/migrations/" in fl or nome.endswith(".sql") or nome in ("models.py", "db.py", "seed.py", "alembic.ini"):
        return "Banco de dados"
    if "/infra/" in fl or nome.startswith(("docker", ".docker")) or nome == "dockerfile" or "/.github/" in fl or nome.endswith(".conf"):
        return "Infraestrutura (Docker, proxy, CI)"
    if "/frontend/" in fl:
        return "Telas (frontend)"
    if "/backend/" in fl:
        return "API e regras de negócio (backend)"
    if "/especificacoes/" in fl:
        return "Especificação"
    if nome.endswith(".md") or "/docs/" in fl:
        return "Documentação"
    return "Outros"


def _n(v: float | None, casas: int = 1) -> str:
    if v is None:
        return "—"
    s = f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s[:-2] if casas == 1 and s.endswith(",0") else s


def _cel(t: Any) -> str:
    return str(t if t is not None else "").replace("|", "/").replace("\n", " ").strip()


def _arquivos_projeto(projeto: str, caminhos: list[str] | None = None) -> list[str]:
    alvos = [f"{projeto}/{c}" for c in caminhos] if caminhos else [projeto]
    try:
        out = git("ls-files", "--", *alvos)
    except ErroFabrica:
        return []
    return [f for f in out.splitlines() if f and not f.endswith(IGNORAR_CODIGO)]


def _linhas(f: str) -> int:
    try:
        with open(RAIZ / f, "rb") as h:
            return sum(1 for _ in h)
    except OSError:
        return 0


def _detalhes_modulo(arquivos: list[str]) -> dict:
    """O que o módulo implementa, lido do próprio código: tabelas, rotas da API e telas."""
    tabelas, rotas, telas = [], [], []
    for f in arquivos:
        try:
            txt = (RAIZ / f).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if f.endswith(".py"):
            tabelas += re.findall(r"op\.create_table\(\s*[\"'](\w+)", txt)
            tabelas += re.findall(r"__tablename__\s*=\s*[\"'](\w+)", txt)
            pref = re.search(r"APIRouter\([^)]*prefix\s*=\s*[\"']([^\"']*)", txt)
            for met, rota in re.findall(r"@\w+\.(get|post|put|patch|delete)\(\s*[\"']([^\"']*)", txt):
                rotas.append(f"{met.upper()} {(pref.group(1) if pref else '') + rota or '/'}")
        if f.endswith(".tsx") and ".test." not in f and "/frontend/" in f:
            telas.append(Path(f).stem)
    uniq = lambda xs: list(dict.fromkeys(xs))
    return {"tabelas": uniq(tabelas), "rotas": uniq(rotas), "telas": uniq(telas)}


def _commits(arquivos_ou_caminho: list[str], inicio: str | None = None, fim: str | None = None) -> list[dict]:
    if not arquivos_ou_caminho:
        return []
    args = ["log", "--date=short", "--pretty=format:%h%x1f%ad%x1f%an%x1f%s"]
    if inicio:
        args.append(f"--since={inicio}T00:00:00")
    if fim:
        args.append(f"--until={fim}T23:59:59")
    try:
        out = git(*args, "--", *arquivos_ou_caminho)
    except ErroFabrica:
        return []
    res = []
    for l in out.splitlines():
        p = l.split("\x1f")
        if len(p) == 4:
            res.append({"sha": p[0], "data": p[1], "autor": p[2], "mensagem": p[3]})
    return res


def _numstat(caminho: str, inicio: str, fim: str) -> dict[str, list[int]]:
    """Linhas adicionadas/removidas por camada no período (git log --numstat)."""
    por: dict[str, list[int]] = {}
    try:
        out = git("log", f"--since={inicio}T00:00:00", f"--until={fim}T23:59:59", "--numstat", "--pretty=format:", "--", caminho)
    except ErroFabrica:
        return por
    for l in out.splitlines():
        p = l.split("\t")
        if len(p) != 3 or p[0] == "-" or p[2].endswith(IGNORAR_CODIGO):
            continue
        c = por.setdefault(camada_arquivo(p[2]), [0, 0, 0])
        c[0] += int(p[0]); c[1] += int(p[1]); c[2] += 1
    return por


def _tecnologias(cdir: Path, contrato: dict, projetos: list[str]) -> list[tuple[str, str, str]]:
    linhas = []
    tec = contrato.get("tecnico") or {}
    if tec.get("tecnologias_obrigatorias"):
        linhas.append(("Exigidas no contrato", ", ".join(map(str, tec["tecnologias_obrigatorias"])), "contrato.yaml"))
    if tec.get("banco_de_dados"):
        linhas.append(("Banco de dados", str(tec["banco_de_dados"]), "contrato.yaml"))
    for pj in projetos:
        base = RAIZ / pj
        for req in sorted(base.glob("**/requirements.txt")):
            if "node_modules" in req.parts:
                continue
            nomes = [re.split(r"[<>=\[;~! ]", l.strip())[0] for l in req.read_text(encoding="utf-8").splitlines()
                     if l.strip() and not l.startswith(("#", "-"))]
            if nomes:
                linhas.append(("Backend (Python)", ", ".join(nomes), rel(req)))
        for pkg in sorted(base.glob("**/package.json")):
            if "node_modules" in pkg.parts:
                continue
            try:
                d = json.loads(pkg.read_text(encoding="utf-8"))
            except ValueError:
                continue
            deps = list((d.get("dependencies") or {}).keys())
            dev = list((d.get("devDependencies") or {}).keys())
            if deps:
                linhas.append(("Frontend (TypeScript/React)", ", ".join(deps), rel(pkg)))
            if dev:
                linhas.append(("Build e testes de tela", ", ".join(dev), rel(pkg)))
        for dc in sorted(base.glob("docker-compose*.yml")):
            imgs = re.findall(r"image:\s*([^\s#]+)", dc.read_text(encoding="utf-8"))
            if imgs:
                linhas.append(("Infraestrutura (contêineres)", ", ".join(dict.fromkeys(imgs)), rel(dc)))
    return linhas


def relatorio_tecnico(cid: str, ref: str | None = None) -> Path:
    """Relatório técnico único para o órgão: UST (contratado, feito, aceito, saldo, a fazer), o que foi feito por módulo
    e em qual item do contrato, tecnologias, código do dia/mês/total, testes, telas e pendências."""
    cdir = dir_contrato(cid)
    contrato = ler_yaml(cdir / "contrato.yaml") or {}
    ref = ref or hoje()
    d0 = date.fromisoformat(ref)
    mes_ini = d0.replace(day=1).isoformat()
    mes_nome = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
                "novembro", "dezembro"][d0.month - 1] + f" de {d0.year}"
    ct = contrato.get("contrato") or {}
    med_c = contrato.get("medicao") or {}
    unidade = med_c.get("modalidade") or "UST"
    contratado = numero(med_c.get("quantidade_contratada"))

    # ordens de serviço e medições
    oss, modulos = [], []
    for osf in sorted((cdir / "os").glob("*.yaml")):
        o = ler_yaml(osf) or {}
        oid = o.get("os") or osf.stem
        med = ler_json(cdir / "medicoes" / f"{oid}.json", {}) or {}
        itens = {i.get("modulo"): i for i in med.get("itens") or []}
        projeto = str(o.get("projeto") or "")
        oss.append({"os": oid, "titulo": o.get("titulo", ""), "projeto": projeto, "medido_em": med.get("medido_em", ""),
                    "aviso": med.get("aviso", ""), "autorizacao": o.get("autorizacao") or {}})
        for m in o.get("modulos") or []:
            mid = m.get("id")
            it = itens.get(mid) or {}
            ev = cdir / "evidencias" / oid / str(mid)
            testes = ler_json(ev / "TESTES.json", {}) or {}
            arqs = _arquivos_projeto(projeto, m.get("caminhos") or []) if projeto else []
            por_camada: dict[str, list[int]] = {}
            for f in arqs:
                c = por_camada.setdefault(camada_arquivo(f), [0, 0])
                c[0] += 1; c[1] += _linhas(f)
            telas_img = sorted((ev / "SCREENSHOTS").glob("*.png"))[:2] if (ev / "SCREENSHOTS").exists() else []
            modulos.append({
                "os": oid, "id": mid, "nome": m.get("nome", ""), "projeto": projeto,
                "item": it.get("item") or m.get("item_tabela") or ", ".join(s.get("codigo", "") for s in m.get("servicos") or []),
                "descricao_item": it.get("descricao_item", ""), "previsto": float(it.get("previsto") or 0),
                "comprovado": float(it.get("comprovado") or 0), "aceito": float(it.get("aceito") or 0),
                "horas": it.get("horas"), "memoria": it.get("memoria", ""), "responsavel": it.get("responsavel") or "sem registro",
                "valor": float(it.get("valor_previsto") or 0), "horas_por_perfil": it.get("horas_por_perfil") or {},
                "medido_em": med.get("medido_em", ""), "medido": bool(it),
                "testes": (testes.get("resumo") or {}), "situacao_testes": testes.get("situacao") or "sem registro",
                "testado_em": testes.get("executado_em", ""), "camadas": por_camada, "detalhes": _detalhes_modulo(arqs),
                "commits": _commits(arqs), "telas": telas_img,
            })

    tot = lambda k, ms=modulos: sum(m[k] for m in ms)
    comprovado, aceito, previsto = tot("comprovado"), tot("aceito"), tot("previsto")
    do_mes = [m for m in modulos if m["medido"] and mes_ini <= m["medido_em"][:10] <= ref]
    de_hoje = [m for m in modulos if m["medido"] and m["medido_em"][:10] == ref]

    # planejamento (datas e UST de cada módulo) -> a fazer e meta diária
    feitos = {m["id"] for m in modulos if m["comprovado"] > 0}
    medidos = {m["id"]: m for m in modulos}
    plano_linhas, a_fazer = [], []
    plan = cdir / "PLANEJAMENTO.csv"
    if plan.exists():
        with open(plan, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if not r.get("modulo"):
                    continue
                est = None
                if r["modulo"] in medidos and medidos[r["modulo"]]["previsto"]:
                    est = medidos[r["modulo"]]["previsto"]
                else:
                    try:
                        est = calcular_servicos(cid, [{"codigo": r.get("servico", ""), "quantidade": float(r.get("quantidade") or 1)}]).get("quantidade")
                    except Exception:  # catálogo sem o item ou sem fórmula: fica sem estimativa
                        est = None
                lin = {"id": r["modulo"], "nome": r.get("nome", ""), "item": r.get("servico", ""), "ust": est,
                       "inicio": r.get("inicio", ""), "prazo": r.get("fim", ""), "responsavel": r.get("responsavel") or "a definir"}
                plano_linhas.append(lin)
                if r["modulo"] not in feitos:
                    a_fazer.append(lin)
    for m in modulos:
        if m["comprovado"] == 0 and m["id"] not in {x["id"] for x in a_fazer}:
            a_fazer.append({"id": m["id"], "nome": m["nome"], "item": m["item"], "ust": m["previsto"] or None,
                            "inicio": "", "prazo": "", "responsavel": m["responsavel"]})
    ust_a_fazer = sum(x["ust"] or 0 for x in a_fazer)

    # pagamentos registrados pela empresa (PAGAMENTOS.csv: data, competencia, ust, valor, documento)
    pagos = []
    if (cdir / "PAGAMENTOS.csv").exists():
        pagos = [r for r in ler_tabela(cdir / "PAGAMENTOS.csv") if r.get("documento")]
    ust_pago = sum(float(numero(r.get("ust")) or 0) for r in pagos)
    valor_pago = sum(float(numero(r.get("valor")) or 0) for r in pagos)
    valor_exec = sum(m["valor"] for m in modulos if m["comprovado"] > 0)
    valor_aceito = sum(m["valor"] * (m["aceito"] / m["previsto"]) for m in modulos if m["previsto"])

    # meta diária: UST de cada módulo planejado dividida pelos dias úteis entre início e fim
    def meta_do_dia(d: date) -> tuple[float, list[str]]:
        total, quais = 0.0, []
        for x in plano_linhas:
            try:
                ini_, fim_ = date.fromisoformat(x["inicio"]), date.fromisoformat(x["prazo"])
            except ValueError:
                continue
            if x["ust"] and ini_ <= d <= fim_ and d.weekday() < 5 and dias_uteis(d, d):
                total += x["ust"] / max(1, dias_uteis(ini_, fim_))
                quais.append(x["id"])
        return total, quais
    executado_no_dia = lambda d: sum(m["comprovado"] for m in modulos if m["medido"] and m["medido_em"][:10] == d.isoformat())
    vig_fim = None
    try:
        vig_fim = date.fromisoformat(str(ct.get("vigencia_fim") or ""))
    except ValueError:
        vig_fim = None

    projetos = list(dict.fromkeys(m["projeto"] for m in modulos if m["projeto"]))
    numero_doc = f"RT-{cid}-{d0.strftime('%Y%m%d')}"
    L = [f"# Relatório Técnico de Execução e Medição — {mes_nome}", ""]

    # 1. situação do contrato: executa -> órgão aceita -> paga
    pct = (lambda v: f"{_n(100 * v / contratado)}%") if contratado else (lambda v: "—")
    falta_plan = max(0.0, (contratado or 0) - comprovado - ust_a_fazer) if contratado else None
    rs = lambda v: brl(v) if v else "—"
    L += ["## 1. Situação do contrato", "",
          "O ciclo é: **a empresa executa → o órgão confere e aceita → o órgão paga**. Cada etapa só avança quando a anterior tem registro.", "",
          f"| Etapa | {unidade} | Valor | Situação |", "|---|---|---|---|",
          f"| Contratado | {_n(contratado) if contratado else 'sem registro'} | — | total do contrato |",
          f"| Executado | {_n(comprovado)} | {rs(valor_exec)} | entregue, testado e auditado; vai para o aceite do órgão |",
          f"| Aceito pelo órgão | {_n(aceito)} | {rs(valor_aceito)} | {'aceite registrado' if aceito else 'próxima etapa: o órgão confere o executado e emite o termo de aceite'} |",
          f"| Pago | {_n(ust_pago)} | {rs(valor_pago)} | {'pagamento registrado' if pagos else 'depois do aceite (registre em PAGAMENTOS.csv)'} |"]
    if contratado:
        L += [f"| **Saldo para executar** | **{_n(contratado - comprovado)}** | | contratado − executado |",
              f"| ↳ já planejado | {_n(ust_a_fazer)} | | {len(a_fazer)} módulo(s) com data (seção 10) |",
              f"| ↳ ainda sem planejamento | {_n(falta_plan)} | | precisa de novas demandas/OS do órgão |"]
    L += ["", f"Em uma frase: de {_n(contratado)} {unidade} contratadas, {_n(comprovado)} já foram executadas "
          f"({pct(comprovado)}); {_n(ust_a_fazer)} estão planejadas e {_n(falta_plan)} ainda não têm demanda." if contratado else
          f"Executado até agora: {_n(comprovado)} {unidade}."]
    for o in oss:
        if o["aviso"]:
            L.append(f"> {o['os']}: {o['aviso']}")
    L.append("")

    # 2. meta diária
    mh, quais = meta_do_dia(d0)
    L += ["## 2. Meta diária", "",
          f"- **Meta de hoje ({d0.strftime('%d/%m/%Y')}):** {_n(mh)} {unidade}" + (f" — módulos previstos para hoje: {', '.join(quais)}." if quais else " — nenhum módulo planejado para hoje."),
          f"- **Executado hoje:** {_n(executado_no_dia(d0))} {unidade}."]
    if contratado and vig_fim and vig_fim >= d0:
        du = dias_uteis(d0, vig_fim)
        L.append(f"- **Ritmo para executar todo o saldo até o fim da vigência ({vig_fim.strftime('%d/%m/%Y')}):** "
                 f"{_n((contratado - comprovado) / max(1, du))} {unidade} por dia útil ({du} dias úteis).")
    L += ["", "Como a meta é calculada: a UST de cada módulo do planejamento é dividida igualmente pelos dias úteis entre a data de início "
          "e a de fim; a meta do dia é a soma dos módulos em andamento naquele dia. O executado entra no dia em que o módulo foi medido.", ""]
    fim_mes = (d0.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    dias_mes = [d0.replace(day=1) + timedelta(days=i) for i in range((fim_mes - d0.replace(day=1)).days + 1)]
    dias_mes = [d for d in dias_mes if dias_uteis(d, d)]
    if plano_linhas or do_mes:
        L += [f"| Dia | Meta ({unidade}) | Executado ({unidade}) | Meta acumulada | Executado acumulado |", "|---|---|---|---|---|"]
        am = ae = 0.0
        for d in dias_mes:
            mt, _ = meta_do_dia(d)
            ex = executado_no_dia(d) if d <= d0 else None
            am += mt
            ae += ex or 0
            if mt or ex:
                L.append(f"| {d.strftime('%d/%m')}{' (hoje)' if d == d0 else ''} | {_n(mt)} | {_n(ex) if ex is not None else 'a executar'} | {_n(am)} | {_n(ae) if d <= d0 else '—'} |")
        L.append("")

    # 2. identificação
    emp = configuracao().get("empresa") or {}
    L += ["## 3. Identificação", "", "| Campo | Informação |", "|---|---|",
          f"| Órgão | {_cel((contrato.get('contratante') or {}).get('orgao') or 'sem registro')} |",
          f"| Contrato | {_cel(ct.get('numero') or cid)} |",
          f"| Objeto | {_cel(ct.get('objeto') or 'sem registro')} |",
          f"| Ordens de serviço | {_cel(', '.join(o['os'] + ' — ' + str(o['titulo']) for o in oss) or 'nenhuma')} |",
          f"| Sistema(s) | {_cel(', '.join(projetos) or 'sem registro')} |",
          f"| Período | {mes_nome} (até {d0.strftime('%d/%m/%Y')}) |",
          f"| Contratada | {_cel(emp.get('razao_social') or 'sem registro')}{' — CNPJ ' + _cel(emp['cnpj']) if emp.get('cnpj') else ''} |",
          f"| Responsável técnico | {_cel(emp.get('responsavel_tecnico') or 'sem registro')} |", ""]

    # 4. equipe técnica (pessoas) e agentes de IA
    equipe = carregar_profissionais(cid) if (cdir / "PROFISSIONAIS.csv").exists() else []
    partic = []
    if (cdir / "PARTICIPACOES.csv").exists():
        partic, _ = carregar_participacoes(cid)
    L += ["## 4. Equipe técnica e agentes de IA", "",
          "Os agentes de IA executam as etapas técnicas; a equipe técnica responde por eles: orienta, revisa e aprova. "
          "Participação individual só aparece quando há registro (commit, revisão, ata ou registro do gestor).", ""]
    if equipe:
        L += ["| Nome | Função | Responsabilidade | Desde | Participações registradas |", "|---|---|---|---|---|"]
        for pe in equipe:
            n_part = [x for x in partic if x["profissional_id"] == pe["id"]]
            tipos = ", ".join(f"{t.lower()} {sum(1 for x in n_part if x['tipo'] == t)}" for t in dict.fromkeys(x["tipo"] for x in n_part))
            L.append(f"| {_cel(pe['nome'])} | {_cel(pe.get('funcao'))} | {_cel(pe.get('responsabilidades') or '—')} | "
                     f"{_cel(pe.get('inicio') or '—')} | {tipos or 'nenhuma ainda'} |")
    else:
        L.append("Equipe técnica: sem registro (cadastre com `fabrica.py profissionais adicionar`).")
    papel = {"autorizacao": "G03 Gestor Contratual", "testes": "G12 Engenheiro de Testes", "commits": "G17 Auditor de Evidências",
             "auditoria": "G17 Auditor de Evidências", "medicao": "G15 Medidor de UST", "relatorios": "G19 Gerador de Relatórios",
             "checklist": "G20 Homologador Técnico", "entrega": "G20 Homologador Técnico"}
    etapa_nome = {"autorizacao": "Conferência da autorização", "testes": "Execução dos testes", "commits": "Registro dos commits",
                  "auditoria": "Auditoria das evidências", "medicao": "Medição", "relatorios": "Relatórios",
                  "checklist": "Checklist de qualidade", "entrega": "Pacote de entrega"}
    for o in oss:
        fl = ler_json(cdir / "fluxos" / f"{o['os']}.json", {}) or {}
        autores = sorted({c["autor"] for m in modulos if m["os"] == o["os"] for c in m["commits"]})
        L += ["", f"**Etapas da {o['os']} executadas pelos agentes:**", "", "| Etapa | Agente (papel na fábrica) | Resultado | Data | Situação |", "|---|---|---|---|---|",
              f"| Código (banco, API, telas, testes) | G06/G07/G08 + gerador de cadastros | commits no git (autor: {', '.join(autores) or 'sem registro'}) | "
              f"{min((c['data'] for m in modulos if m['os'] == o['os'] for c in m['commits']), default='—')} | concluído |"]
        for no in NOS_FLUXO:
            info = (fl.get("nos") or {}).get(no) or {}
            st = {"CONCLUIDO": "concluído", "PAUSA": "aguardando a equipe", "PENDENTE": "pendente", "FALHA": "falhou"}.get(info.get("status"), "sem registro")
            L.append(f"| {etapa_nome[no]} | {papel[no]} | {_cel(info.get('resultado') or '—')} | {(info.get('fim') or info.get('inicio') or '—')[:10]} | {st} |")
        o["pausa"] = next((((fl.get("nos") or {}).get(no) or {}).get("resultado") for no in NOS_FLUXO
                           if (((fl.get("nos") or {}).get(no) or {}).get("status") == "PAUSA")), None)
    L.append("")

    # 3. o que foi feito
    L += ["## 5. O que foi feito e quanto foi medido", "",
          f"| Módulo | O que foi entregue | Item do contrato | {unidade} executada | Testes |", "|---|---|---|---|---|"]
    for m in modulos:
        ent = ", ".join(k.split(" (")[0] for k in m["camadas"] if k not in ("Outros", "Especificação", "Documentação")) or "sem registro"
        t = m["testes"]
        tt = f"{t.get('testes', 0)} ok, {t.get('falhas', 0) + t.get('erros', 0)} falha(s)" if t else "sem registro"
        L.append(f"| {m['id']} — {_cel(m['nome'])} | {_cel(ent)} | {_cel(m['item'])} | {_n(m['comprovado'])} | {tt} |")
    L.append(f"| **Total** | | | **{_n(comprovado)}** | |")
    L.append("")
    for m in modulos:
        L += [f"### {m['id']} — {m['nome']}", ""]
        d = m["detalhes"]
        if "Banco de dados" in m["camadas"]:
            L.append(f"- **Banco de dados:** {('tabela(s) ' + ', '.join('`' + x + '`' for x in d['tabelas'])) if d['tabelas'] else 'estrutura e acesso a dados'}"
                     f" — {m['camadas']['Banco de dados'][0]} arquivo(s), {m['camadas']['Banco de dados'][1]} linhas.")
        api = m["camadas"].get("API e regras de negócio (backend)")
        if api:
            rotas = d["rotas"]
            L.append(f"- **API (backend):** {len(rotas)} rota(s){': ' + ', '.join('`' + r + '`' for r in rotas[:8]) if rotas else ''}"
                     f"{' e outras' if len(rotas) > 8 else ''} — {api[0]} arquivo(s), {api[1]} linhas.")
        tel = m["camadas"].get("Telas (frontend)")
        if tel:
            L.append(f"- **Telas (frontend):** {', '.join(d['telas'][:8]) or 'componentes de tela'} — {tel[0]} arquivo(s), {tel[1]} linhas.")
        inf = m["camadas"].get("Infraestrutura (Docker, proxy, CI)")
        if inf:
            L.append(f"- **Infraestrutura:** {inf[0]} arquivo(s), {inf[1]} linhas.")
        tst = m["camadas"].get("Testes automatizados")
        t = m["testes"]
        L.append(f"- **Testes:** {t.get('testes', 0)} executado(s), {t.get('falhas', 0) + t.get('erros', 0)} falha(s) — "
                 f"{m['situacao_testes']}{' em ' + m['testado_em'][:10] if m['testado_em'] else ''}"
                 f"{f' ({tst[0]} arquivo(s) de teste, {tst[1]} linhas)' if tst else ''}." if t else "- **Testes:** sem registro.")
        L.append(f"- **Medição:** item {m['item']}{' — ' + m['descricao_item'] if m['descricao_item'] else ''}: "
                 f"previsto {_n(m['previsto'])}, executado **{_n(m['comprovado'])}**, aceito {_n(m['aceito'])} {unidade}"
                 f"{'; ' + _n(m['horas']) + ' h pelo catálogo' if m['horas'] else ''}.")
        if m["commits"]:
            L.append("- **Commits:** " + "; ".join(f"`{c['sha']}` {c['data']} {_cel(c['mensagem'])}" for c in m["commits"][:4])
                     + (f" (+{len(m['commits']) - 4})" if len(m["commits"]) > 4 else "") + ".")
        resp = m["responsavel"]
        if resp in ("A CADASTRAR", "sem registro"):
            resp = (f"equipe técnica ({', '.join(pe['nome'] for pe in equipe)}); revisão individual deste módulo: sem registro"
                    if equipe else "sem registro")
        L.append(f"- **Responsável:** {resp}.")
        for img in m["telas"]:
            L += ["", f"![{m['id']} — {img.stem.split('-', 1)[-1].replace('-', ' ')} (preview)]({os.path.relpath(img, cdir / 'relatorios')})"]
        L.append("")

    # 5. de onde vêm os números
    _, perfis_c, med_cfg = catalogo(cid)
    formula = str(med_cfg.get("formula") or "").upper()
    nome_perfil = lambda k: re.sub(r"\s*\(.*\)$", "", (perfis_c.get(k) or {}).get("descricao") or k.replace("_", " ").capitalize())
    L += ["## 6. De onde vêm os números (memória de cálculo)", "",
          "1. **O contrato define o catálogo de serviços** (`CATALOGO_SERVICOS.csv`): para cada serviço, quantas horas de cada perfil ele consome.",
          "2. **Cada perfil tem um fator de UST por hora e um valor por hora** (`PERFIS.csv`)." if formula == "HORAS_X_FATOR" else
          "2. **Cada serviço do catálogo tem uma quantidade fixa de UST** (`CATALOGO_SERVICOS.csv`)." if formula == "UST_POR_SERVICO" else
          "2. **A quantidade de cada módulo está definida na OS / tabela do contrato** (`TABELA_UST.csv`).",
          f"3. **A fórmula do contrato é `{formula or 'definida na OS'}`**" + (": UST do serviço = soma de (horas do perfil × fator do perfil)." if formula == "HORAS_X_FATOR" else "."),
          "4. **A OS diz quais serviços cada módulo usa.**",
          "5. **O módulo só conta como executado** quando o código está no git, os testes passaram e a auditoria das evidências aprovou. "
          "Linhas de código não entram na conta.", "",
          f"| Módulo | Serviço | Conta | {unidade} | Valor |", "|---|---|---|---|---|"]
    for m in modulos:
        hp = m["horas_por_perfil"]
        if formula == "HORAS_X_FATOR" and hp:
            conta = " + ".join(f"{_n(h)} h {nome_perfil(k)} × {_n(numero((perfis_c.get(k) or {}).get('fator_ust_por_hora')), 2).rstrip('0').rstrip(',')}"
                               for k, h in hp.items())
        elif m["memoria"]:
            conta = m["memoria"].split(";")[0]
        else:
            conta = "sem registro de medição"
        L.append(f"| {m['id']} | {_cel(m['item'])} | {_cel(conta)} | {_n(m['previsto'])} | {rs(m['valor'])} |")
    L += ["", "Exemplo de leitura: \"4 h Analista × 1,2\" significa 4 horas do perfil Analista, que valem 1,2 UST por hora = 4,8 UST.", ""]

    # 4. tecnologias
    L += ["## 7. Tecnologias utilizadas", "", "| Camada | Tecnologias | Fonte |", "|---|---|---|"]
    for camada, nomes, fonte in _tecnologias(cdir, contrato, projetos) or [("—", "sem registro", "—")]:
        L.append(f"| {camada} | {_cel(nomes)} | `{fonte}` |")
    L.append("")

    # 5. código do mês e de hoje / 6. código total
    for titulo, ini in ((f"## 8. Código de {mes_nome}", mes_ini), (f"### Código de hoje ({d0.strftime('%d/%m/%Y')})", ref)):
        L += [titulo, ""]
        for pj in projetos:
            cs = _commits([pj], ini, ref)
            ns = _numstat(pj, ini, ref)
            L.append(f"**{pj}:** {len(cs)} commit(s), +{sum(v[0] for v in ns.values())} / −{sum(v[1] for v in ns.values())} linhas.")
            if ns:
                L += ["", "| Camada | Arquivos alterados | Linhas adicionadas | Linhas removidas |", "|---|---|---|---|"]
                for k, v in sorted(ns.items(), key=lambda kv: -kv[1][0]):
                    L.append(f"| {k} | {v[2]} | {v[0]} | {v[1]} |")
            if cs and ini == mes_ini:
                L += ["", "| Commit | Data | Descrição |", "|---|---|---|"]
                for c in cs[:40]:
                    L.append(f"| `{c['sha']}` | {c['data']} | {_cel(c['mensagem'])[:110]} |")
                if len(cs) > 40:
                    L.append(f"| … | | mais {len(cs) - 40} commit(s) no git |")
            L.append("")
    L += ["## 9. Código total do sistema", ""]
    for pj in projetos:
        arqs = _arquivos_projeto(pj)
        por_c: dict[str, list[int]] = {}
        por_l: dict[str, list[int]] = {}
        for f in arqs:
            n = _linhas(f)
            c = por_c.setdefault(camada_arquivo(f), [0, 0]); c[0] += 1; c[1] += n
            lang = "Docker" if Path(f).name.lower().startswith("dockerfile") else EXT_TEXTO.get(Path(f).suffix.lower(), "Outros")
            g = por_l.setdefault(lang, [0, 0]); g[0] += 1; g[1] += n
        L += [f"**{pj}:** {len(arqs)} arquivo(s), {sum(v[1] for v in por_c.values())} linhas, "
              f"{len(_commits([pj]))} commit(s) desde o início.", "",
              "| Camada | Arquivos | Linhas |", "|---|---|---|"]
        L += [f"| {k} | {v[0]} | {v[1]} |" for k, v in sorted(por_c.items(), key=lambda kv: -kv[1][1])]
        L += ["", "| Linguagem | Arquivos | Linhas |", "|---|---|---|"]
        L += [f"| {k} | {v[0]} | {v[1]} |" for k, v in sorted(por_l.items(), key=lambda kv: -kv[1][1])]
        L.append("")
    L += ["> Linhas de código e commits mostram o tamanho do trabalho; a quantidade medida vem do catálogo do contrato, não das linhas.", ""]

    # 9. a fazer (planejado)
    L += ["## 10. A fazer (planejado)", ""]
    if a_fazer:
        L += [f"| Módulo | O que fazer | Item do contrato | {unidade} (estimativa) | Início | Fim | Responsável |", "|---|---|---|---|---|---|---|"]
        L += [f"| {x['id']} | {_cel(x['nome'])} | {_cel(x['item'])} | {_n(x['ust'])} | {_cel(x['inicio']) or '—'} | {_cel(x['prazo']) or '—'} | {_cel(x['responsavel'])} |" for x in a_fazer]
        L += ["", f"Total planejado: {_n(ust_a_fazer)} {unidade} (estimativa pelo catálogo; vira executado quando entregue e medido)."]
    else:
        L.append("Nenhum módulo planejado além do que já foi executado.")
    L.append("")

    # 8. pendências
    pend = []
    if aceito < comprovado:
        pend.append(f"Próxima etapa normal: enviar ao órgão os {_n(comprovado - aceito)} {unidade} executados para conferência e termo de aceite.")
    if aceito > ust_pago:
        pend.append(f"Faturar e acompanhar o pagamento de {_n(aceito - ust_pago)} {unidade} aceitos.")
    for o in oss:
        if o.get("pausa"):
            pend.append(f"{o['os']}: a equipe técnica verifica o checklist — {o['pausa']}.")
    sem_resp = [m["id"] for m in modulos if m["responsavel"] in ("A CADASTRAR", "sem registro")]
    if sem_resp:
        pend.append(f"Registrar a revisão de cada módulo por um membro da equipe ({', '.join(sem_resp)}) em PARTICIPACOES.csv "
                    "(data, pessoa, módulo, tipo REVISAO/APROVACAO, evidência).")
    sem_teste = [m["id"] for m in modulos if not m["testes"]]
    if sem_teste:
        pend.append(f"Módulos sem teste registrado: {', '.join(sem_teste)}.")
    for o in oss:
        if not (o["autorizacao"] or {}).get("autorizado"):
            pend.append(f"{o['os']} sem autorização registrada.")
    L += ["## 11. Próximas etapas e pendências", ""] + [f"- {p}" for p in pend or ["Nenhuma pendência registrada."]] + [""]
    L += ["## 12. Arquivos de origem", "",
          "- UST: `medicoes/<OS>.json` (medição pelo catálogo do contrato) e `contrato.yaml`.",
          "- O que foi feito, código e commits: repositório git (`git log`, `git ls-files`).",
          "- Testes: `evidencias/<OS>/<MÓDULO>/TESTES.json` (execuções reais com JUnit).",
          "- Telas: capturas reais em `evidencias/<OS>/<MÓDULO>/SCREENSHOTS/`.",
          "- A fazer e meta diária: `PLANEJAMENTO.csv` (estimativa pelo catálogo, datas de início e fim).",
          "- Pagamentos: `PAGAMENTOS.csv` (data, competência, UST, valor e documento do pagamento).", ""]

    out = cdir / "relatorios" / f"RELATORIO_TECNICO_{ref}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    gravar_json(out.with_suffix(".json"), {
        "contrato": cid, "data": ref, "numero": numero_doc, "unidade": unidade, "contratado": contratado, "previsto": previsto,
        "comprovado": comprovado, "aceito": aceito, "mes": tot("comprovado", do_mes), "hoje": tot("comprovado", de_hoje),
        "a_fazer": ust_a_fazer, "saldo": (contratado - comprovado) if contratado else None, "pago": ust_pago,
        "meta_hoje": round(meta_do_dia(d0)[0], 2), "executado_hoje": executado_no_dia(d0),
        "modulos": [{k: m[k] for k in ("os", "id", "nome", "item", "previsto", "comprovado", "aceito")} for m in modulos]})
    exportar_word(out, cid, periodo=mes_nome, classificacao="Documento para o órgão", subtitulo="Tecnologias, UST, código e telas",
                  numero_doc=numero_doc, data_doc=ref, assinar=True)
    return out



# ------------------------------------------------------- sistema (formulário -> código completo)

PERMISSOES_PADRAO = {"ler": ["ADMIN", "GESTOR", "OPERADOR", "CONSULTA"], "escrever": ["ADMIN", "GESTOR", "OPERADOR"],
                     "excluir": ["ADMIN", "GESTOR"]}


def _ler_sistema(arquivo: Path) -> tuple[dict, Path]:
    d = ler_yaml(arquivo) or {}
    s = d.get("sistema") or {}
    if not s.get("nome"):
        raise ErroFabrica("formulário sem sistema.nome (veja fabrica/templates/SISTEMA.yaml)")
    mods = d.get("modulos") or []
    if not mods:
        raise ErroFabrica("formulário sem módulos")
    ids = [m.get("id") for m in mods]
    for i in ids:
        if not re.fullmatch(r"MOD-\d{3}", str(i or "")):
            raise ErroFabrica(f"id de módulo inválido: {i!r} (use MOD-NNN)")
    if len(set(ids)) != len(ids):
        raise ErroFabrica("ids de módulo repetidos")
    pasta = PROJETOS / (s.get("pasta") or slug(s["nome"]))
    return d, pasta


def _spec_modulo(m: dict) -> dict:
    c = m["cadastro"]
    return {"entidade": c.get("entidade"), "tabela": c.get("tabela"), "rotulo": c.get("rotulo") or m.get("nome"),
            "modulo": m["id"], "campos": c.get("campos") or [], "permissoes": c.get("permissoes") or PERMISSOES_PADRAO}


def _rodar(cmd: list[str], cwd: Path, env: dict | None = None, timeout: int = 900) -> tuple[int, str]:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env={**os.environ, **(env or {})})
    return r.returncode, (r.stdout + r.stderr)


def sistema_gerar(arquivo: Path, testar: bool = True) -> dict:
    """Gera o sistema do formulário: base (login, perfis, auditoria, Docker) + um módulo completo por cadastro."""
    sys.path.insert(0, str(Path(__file__).parent))
    from gerador_crud import ErroGerador, gerar_crud, validar_spec
    d, pasta = _ler_sistema(arquivo)
    s = d["sistema"]
    criado = False
    if not (pasta / "backend" / "app" / "modulos" / "__init__.py").exists():
        criar_componente("sistema-gov", pasta, s["nome"])
        criado = True
    (pasta / "SISTEMA.yaml").write_text(arquivo.read_text(encoding="utf-8"), encoding="utf-8")
    res = {"sistema": s["nome"], "pasta": rel(pasta), "base_criada": criado, "modulos": [], "testes": {}}
    for m in d["modulos"]:
        item = {"id": m["id"], "nome": m.get("nome", ""), "servico": m.get("servico", ""), "o_que_faz": m.get("o_que_faz", "")}
        if not m.get("cadastro"):
            item["situacao"] = "PRECISA DE ESPECIFICAÇÃO (não é cadastro: relatório, integração ou regra especial)"
            res["modulos"].append(item)
            continue
        spec = _spec_modulo(m)
        try:
            validar_spec(spec)
        except ErroGerador as e:
            raise ErroFabrica(f"{m['id']}: {e}")
        if (pasta / "backend" / "app" / "modulos" / spec["tabela"]).exists():
            item["situacao"] = "GERADO"
        else:
            sp = pasta / "especificacoes" / f"{spec['tabela']}.yaml"
            sp.parent.mkdir(parents=True, exist_ok=True)
            sp.write_text(yaml.safe_dump(spec, allow_unicode=True, sort_keys=False), encoding="utf-8")
            try:
                item["arquivos"] = gerar_crud(sp, pasta)
            except ErroGerador as e:
                raise ErroFabrica(f"{m['id']}: {e}")
            item["situacao"] = "GERADO"
        tab, ent = spec["tabela"], spec["entidade"]
        item["caminhos"] = [f"backend/app/modulos/{tab}", *[str(p.relative_to(pasta)) for p in sorted((pasta / "backend" / "migrations" / "versions").glob(f"*_{tab}.py"))],
                            f"backend/tests/test_{m['id'].lower().replace('-', '')}_{tab}.py", f"frontend/src/modulos/{tab}", f"especificacoes/{tab}.yaml"]
        item["testes"] = [
            {"nome": "backend", "cwd": "backend", "cmd": ["python3", "-m", "pytest", item["caminhos"][-3].removeprefix("backend/"), "-v", "--junitxml={junit}"]},
            {"nome": "frontend", "cwd": "frontend", "cmd": ["npx", "vitest", "run", f"src/modulos/{tab}/{ent}Pagina.test.tsx",
                                                          "--reporter=default", "--reporter=junit", "--outputFile.junit={junit}"]}]
        res["modulos"].append(item)
    # bloco pronto para a OS (medição liga módulo -> item do catálogo -> caminhos -> testes)
    blocos = [{"id": m["id"], "nome": m["nome"], "servicos": [{"codigo": m["servico"], "quantidade": 1.0}] if m.get("servico") else [],
               "tem_interface": True, "caminhos": m.get("caminhos", []), "testes": m.get("testes", [])}
              for m in res["modulos"] if m.get("caminhos")]
    (pasta / "MODULOS_OS.yaml").write_text(
        "# Módulos gerados do formulário, prontos para colar na OS AUTORIZADA (contratos/<C>/os/<OS>.yaml -> modulos).\n"
        + yaml.safe_dump({"modulos": blocos}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    if testar:
        env = {"TEST_DATABASE_URL": os.environ["TEST_DATABASE_URL"]} if os.environ.get("TEST_DATABASE_URL") else {}
        cod, out = _rodar([sys.executable, "-m", "pytest", "-q", "-o", "addopts="], pasta / "backend", env)
        res["testes"]["backend"] = {"codigo_saida": cod, "resumo": next((l.strip("= ") for l in reversed(out.splitlines())
                                                                     if re.search(r"\d+ (passed|failed)", l)), out.strip()[-200:]),
                                    "banco": "PostgreSQL" if env else "SQLite"}
        fe = pasta / "frontend"
        if not (fe / "node_modules").exists():
            cod_i, out_i = _rodar(["npm", "install", "--no-audit", "--no-fund"], fe, timeout=1800)
            if cod_i:
                res["testes"]["frontend"] = {"codigo_saida": cod_i, "resumo": "npm install falhou: " + out_i.strip()[-300:]}
        if "frontend" not in res["testes"]:
            cod, out = _rodar(["npx", "vitest", "run"], fe)
            linha = [l for l in out.splitlines() if "Tests" in l and ("passed" in l or "failed" in l)]
            res["testes"]["frontend"] = {"codigo_saida": cod, "resumo": (linha[-1].strip() if linha else out.strip()[-200:])}
            cod, out = _rodar(["npm", "run", "build"], fe)
            res["testes"]["build"] = {"codigo_saida": cod, "resumo": "build OK" if cod == 0 else out.strip()[-300:]}
    # documentação dos módulos
    L = [f"# {s['nome']} — módulos", "", f"{s.get('objetivo', '')}", "",
         "| Módulo | O que faz | Item do catálogo | Situação |", "|---|---|---|---|"]
    L += [f"| {m['id']} — {m['nome']} | {_cel(m['o_que_faz'])} | {m['servico'] or '—'} | {m['situacao']} |" for m in res["modulos"]]
    if res["testes"]:
        L += ["", "## Testes executados", "", "| Etapa | Resultado | Código de saída |", "|---|---|---|"]
        L += [f"| {k} | {_cel(v['resumo'])} | {v['codigo_saida']} |" for k, v in res["testes"].items()]
    (pasta / "docs").mkdir(exist_ok=True)
    (pasta / "docs" / "MODULOS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    # README do sistema a partir do formulário; mantém as instruções de execução da base
    readme = pasta / "README.md"
    base_txt = readme.read_text(encoding="utf-8") if readme.exists() else ""
    cauda = base_txt[base_txt.find("## Opção A"):] if "## Opção A" in base_txt else ""
    cauda = re.sub(r"projetos/[a-z0-9-]+", rel(pasta), cauda)
    R = [f"# {s['nome']}", "", s.get("objetivo", ""), "", f"- Órgão: {s.get('orgao') or 'a definir'}",
         f"- Contrato: {s.get('contrato') or 'a definir'}", f"- Usuários: {s.get('usuarios') or 'a definir'}", "",
         "| Camada | Tecnologia |", "|---|---|", "| Frontend | React + TypeScript + Vite (servido por Nginx) |",
         "| Backend | Python + FastAPI + SQLAlchemy 2 + Alembic |", "| Banco | PostgreSQL 16 |",
         "| Infra | Docker Compose; Nginx com TLS para produção |", "",
         "## Módulos", "", "| Módulo | O que faz | Situação |", "|---|---|---|",
         "| Base | Login, perfis, usuários, auditoria, documentos, pesquisa e painel | pronta (stack sistema-gov) |"]
    R += [f"| {m['id']} — {m['nome']} | {_cel(m['o_que_faz'])} | {m['situacao']} |" for m in res["modulos"]]
    R += ["", "Formulário de origem: `SISTEMA.yaml`. Detalhes e testes: `docs/MODULOS.md`. Telas: `docs/PREVIEW.md`.", ""]
    readme.write_text("\n".join(R) + "\n" + cauda, encoding="utf-8")
    gravar_json(pasta / "docs" / "GERACAO.json", res)
    return res


def sistema_preview(arquivo: Path, porta_api: int = 8100, porta_web: int = 5180) -> dict:
    """Sobe o sistema com dados fictícios, cria registros pela tela e captura as telas reais de cada módulo."""
    sys.path.insert(0, str(Path(__file__).parent))
    from gerador_crud import _valor
    import secrets
    import tempfile
    import time
    import urllib.request
    d, pasta = _ler_sistema(arquivo)
    be, fe = pasta / "backend", pasta / "frontend"
    if not (be / "app" / "modulos").exists():
        raise ErroFabrica("gere o sistema antes: fabrica.py sistema gerar <formulário>")
    tmp = Path(tempfile.mkdtemp(prefix="preview-"))
    db_url = os.environ.get("PREVIEW_DATABASE_URL") or f"sqlite:///{tmp / 'preview.db'}"
    email, senha = "admin@demo.gov.br", "Prev" + secrets.token_hex(6) + "9a"
    env = {"DATABASE_URL": db_url, "APP_ENV": "dev", "ADMIN_EMAIL": email, "ADMIN_SENHA": senha, "DEMO": "1",
           "UPLOAD_DIR": str(tmp / "uploads"), "CORS_ORIGINS": f"http://127.0.0.1:{porta_web}"}
    for cmd in ([sys.executable, "-m", "alembic", "upgrade", "head"], [sys.executable, "-m", "app.seed"]):
        cod, out = _rodar(cmd, be, env)
        if cod:
            raise ErroFabrica(f"preview: {' '.join(cmd[2:])} falhou: {out.strip()[-400:]}")
    mods = []
    for m in d["modulos"]:
        if not m.get("cadastro"):
            continue
        sp = _spec_modulo(m)
        mods.append({"id": m["id"], "rotulo": sp["rotulo"], "tabela": sp["tabela"],
                     "campos": [{"id": f"{sp['tabela']}-{c['nome']}", "tipo": c["tipo"], "obrigatorio": bool(c.get("obrigatorio")),
                                 "valores": [_valor(c, i) for i in range(2)]} for c in sp["campos"]]})
    plano = tmp / "plano.json"
    plano.write_text(json.dumps({"modulos": mods}, ensure_ascii=False), encoding="utf-8")
    destino = pasta / "docs" / "preview"
    destino.mkdir(parents=True, exist_ok=True)
    api = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(porta_api)],
                           cwd=be, env={**os.environ, **env}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    web = subprocess.Popen(["npx", "vite", "--host", "127.0.0.1", "--port", str(porta_web), "--strictPort"], cwd=fe,
                           env={**os.environ, "API_URL": f"http://127.0.0.1:{porta_api}"}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for url in (f"http://127.0.0.1:{porta_api}/api/health", f"http://127.0.0.1:{porta_web}/"):
            for _ in range(120):
                try:
                    urllib.request.urlopen(url, timeout=2)
                    break
                except Exception:
                    time.sleep(0.5)
            else:
                raise ErroFabrica(f"preview: {url} não respondeu")
        cod, out = _rodar(["node", str(FAB / "ferramentas" / "preview_sistema.cjs"), f"http://127.0.0.1:{porta_web}", str(plano),
                           str(destino), email, senha], RAIZ, timeout=600)
    finally:
        for p in (api, web):
            p.terminate()
        for p in (api, web):
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                p.kill()
        shutil.rmtree(tmp, ignore_errors=True)
    if cod:
        raise ErroFabrica(f"preview: captura falhou: {out.strip()[-600:]}")
    telas = sorted(str(p.relative_to(RAIZ)) for p in destino.glob("*.png"))
    L = [f"# Preview — {d['sistema']['nome']}", "", "Telas reais capturadas com o sistema rodando localmente, com dados fictícios",
         f"(registros criados pela própria tela). URL publicada: NÃO PUBLICADA.", ""]
    L += [f"![{Path(t).stem}](preview/{Path(t).name})" for t in telas]
    (pasta / "docs" / "PREVIEW.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return {"telas": telas, "log": out.strip().splitlines()[-5:]}


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
    x.add_argument("tipo", choices=["diario", "semanal", "mensal", "profissional", "tecnico"]); x.add_argument("contrato")
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
    x = sp.add_parser("config", help="Configuração central (CONFIGURACAO_FABRICA.yaml)"); x.add_argument("sub", choices=["verificar", "mostrar"])
    x = sp.add_parser("capacidade", help="ESTIMATIVA de produção por pessoa/dia/mês (UST, PF, horas, valor)"); x.add_argument("contrato")
    x.add_argument("--dias", type=int, default=21); x.add_argument("--simular", default="", help='ex.: "DESENVOLVEDOR_PLENO=3,ANALISTA_TESTES=1"')
    x = sp.add_parser("fluxo", help="Executa a OS do começo ao fim (checkpoints, pausas humanas)"); x.add_argument("contrato"); x.add_argument("os")
    x.add_argument("--do-zero", action="store_true"); x.add_argument("--aprovado-por", default=""); x.add_argument("--ate", choices=NOS_FLUXO)
    x = sp.add_parser("gec", help="Gera o GEC completo (Word)"); x.add_argument("contrato")
    x = sp.add_parser("proximo-passo", help="O que falta e o que fazer agora (do começo ao fim)"); x.add_argument("contrato", nargs="?"); x.add_argument("--data")
    x = sp.add_parser("abertura", help="Abertura do dia (contratado, saldo, equipe, plano do dia)"); x.add_argument("contrato"); x.add_argument("--data")
    pj = sp.add_parser("planejamento", help="Plano por projeto (UST, horas, perfis, prazos, capacidade)").add_subparsers(dest="sub", required=True)
    x = pj.add_parser("consolidar"); x.add_argument("contrato"); x.add_argument("--horas-dia", type=float, default=8.0)
    x = pj.add_parser("gerar-os"); x.add_argument("contrato"); x.add_argument("--projeto", required=True); x.add_argument("--os", required=True)
    x.add_argument("--caminho", required=True, help="pasta do código do projeto, ex.: projetos/gestao-documental")
    ss = sp.add_parser("sistema", help="Formulário do sistema -> código completo (banco, API, telas, testes) e preview").add_subparsers(dest="sub", required=True)
    x = ss.add_parser("gerar"); x.add_argument("formulario"); x.add_argument("--sem-testes", action="store_true")
    x = ss.add_parser("preview"); x.add_argument("formulario"); x.add_argument("--porta-api", type=int, default=8100)
    x.add_argument("--porta-web", type=int, default=5180)
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
            if a.tipo == "tecnico":
                print(rel(relatorio_tecnico(a.contrato, a.data)))
            else:
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
        elif a.cmd == "config":
            if a.sub == "mostrar":
                print(yaml.safe_dump(configuracao(), allow_unicode=True, sort_keys=False))
            else:
                av = verificar_configuracao(); print("\n".join(f"aviso: {x}" for x in av) or "OK: configuração válida")
        elif a.cmd == "capacidade":
            print(rel(capacidade(a.contrato, a.dias, a.simular)))
        elif a.cmd == "fluxo":
            e = fluxo(a.contrato, a.os, retomar=not a.do_zero, aprovado_por=a.aprovado_por, ate=a.ate)
            for n, i in e["nos"].items():
                print(f"{n:11} {i['status']:10} {i.get('resultado') or i.get('erro') or ''}")
            print(f"\nSituação: {e['situacao']}")
        elif a.cmd == "gec":
            print(rel(gec(a.contrato)))
        elif a.cmd == "proximo-passo":
            print(texto_proximo_passo(proximo_passo(a.contrato, a.data)))
        elif a.cmd == "abertura":
            print(rel(abertura(a.contrato, a.data)))
        elif a.cmd == "planejamento":
            if a.sub == "consolidar":
                print(rel(planejamento(a.contrato, a.horas_dia)))
            else:
                print(rel(gerar_os_do_plano(a.contrato, a.projeto, a.os, a.caminho)))
        elif a.cmd == "sistema":
            if a.sub == "gerar":
                print(json.dumps(sistema_gerar(Path(a.formulario), testar=not a.sem_testes), ensure_ascii=False, indent=2))
            else:
                print(json.dumps(sistema_preview(Path(a.formulario), a.porta_api, a.porta_web), ensure_ascii=False, indent=2))
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
