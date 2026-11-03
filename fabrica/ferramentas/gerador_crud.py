"""Gerador de CRUD completo para a stack python-fastapi + react-vite da fábrica.

A partir de uma especificação YAML de entidade, gera código REAL, separado por módulo:
  backend/app/modulos/<tabela>/{__init__,models,schemas,router}.py
  backend/migrations/versions/<rev>_<tabela>.py            (migração Alembic)
  backend/tests/test_<mod>_<tabela>.py                      (testes de API)
  frontend/src/modulos/<tabela>/{api.ts,<Ent>Pagina.tsx,<Ent>Pagina.test.tsx}
e registra rota + menu no App.tsx. O código gerado é ponto de partida revisável, não caixa-preta.

Especificação (exemplo):
  entidade: Interessado          # nome da classe (PascalCase)
  tabela: interessados           # nome da tabela e do pacote
  rotulo: Interessados           # texto do menu/tela
  modulo: MOD-101
  campos:
    - {nome: nome, tipo: texto, max: 150, obrigatorio: true, busca: true}
    - {nome: documento, tipo: cpf_cnpj, obrigatorio: true, unico: true, busca: true, pessoal: true}
    - {nome: tipo_pessoa, tipo: enum, opcoes: [FISICA, JURIDICA], obrigatorio: true}
    - {nome: interessado_id, tipo: referencia, alvo: interessados, obrigatorio: true}
  permissoes: {ler: [ADMIN, GESTOR, OPERADOR, CONSULTA], escrever: [ADMIN, GESTOR, OPERADOR], excluir: [ADMIN, GESTOR]}

Tipos: texto, texto_longo, inteiro, decimal, data, booleano, email, cpf_cnpj, enum, referencia.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

TIPOS = {"texto", "texto_longo", "inteiro", "decimal", "data", "booleano", "email", "cpf_cnpj", "enum", "referencia"}
PERFIS = ["ADMIN", "GESTOR", "OPERADOR", "CONSULTA"]
CPFS_VALIDOS = ["52998224725", "11144477735", "39053344705", "15350946056"]


class ErroGerador(ValueError):
    pass


# ----------------------------------------------------------------- especificação

def carregar_spec(p: Path) -> dict:
    s = yaml.safe_load(p.read_text(encoding="utf-8"))
    validar_spec(s)
    return s


def validar_spec(s: dict) -> None:
    for k in ("entidade", "tabela", "rotulo", "modulo", "campos"):
        if not s.get(k):
            raise ErroGerador(f"especificação sem '{k}'")
    if not re.fullmatch(r"[A-Z][A-Za-z0-9]+", s["entidade"]):
        raise ErroGerador("entidade deve ser PascalCase (ex.: Interessado)")
    if not re.fullmatch(r"[a-z][a-z0-9_]+", s["tabela"]):
        raise ErroGerador("tabela deve ser minúscula com _ (ex.: interessados)")
    nomes = set()
    for c in s["campos"]:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", c.get("nome", "")):
            raise ErroGerador(f"nome de campo inválido: {c.get('nome')}")
        if c["nome"] in ("id", "ativo", "criado_em", "atualizado_em") or c["nome"] in nomes:
            raise ErroGerador(f"campo reservado ou duplicado: {c['nome']}")
        nomes.add(c["nome"])
        if c.get("tipo") not in TIPOS:
            raise ErroGerador(f"tipo inválido em {c['nome']}: {c.get('tipo')} (use {sorted(TIPOS)})")
        if c["tipo"] == "enum" and not c.get("opcoes"):
            raise ErroGerador(f"enum {c['nome']} sem opcoes")
        if c["tipo"] == "referencia" and not c.get("alvo"):
            raise ErroGerador(f"referencia {c['nome']} sem alvo")
    perm = s.setdefault("permissoes", {})
    perm.setdefault("ler", PERFIS)
    perm.setdefault("escrever", ["ADMIN", "GESTOR", "OPERADOR"])
    perm.setdefault("excluir", ["ADMIN", "GESTOR"])
    for k, v in perm.items():
        if any(p not in PERFIS for p in v):
            raise ErroGerador(f"perfil inválido em permissoes.{k}")


def _mod_slug(s: dict) -> str:
    return re.sub(r"[^a-z0-9]", "", s["modulo"].lower())  # MOD-101 -> mod101


def _rotulo_campo(c: dict) -> str:
    return c.get("rotulo") or c["nome"].replace("_id", "").replace("_", " ").capitalize()


def _max(c: dict) -> int:
    return int(c.get("max") or {"texto": 200, "texto_longo": 5000, "email": 254}.get(c["tipo"], 200))


# ----------------------------------------------------------------- backend

def _coluna_sa(c: dict) -> tuple[str, str]:
    """(anotação Python, expressão mapped_column)"""
    opc = "" if c.get("obrigatorio") else " | None"
    extra = []
    if c.get("unico"):
        extra += ["unique=True", "index=True"]
    elif c.get("busca") or c["tipo"] == "referencia":
        extra.append("index=True")
    if not c.get("obrigatorio"):
        extra.append("nullable=True")
    sfx = (", " + ", ".join(extra)) if extra else ""
    t = c["tipo"]
    if t in ("texto", "email"):
        return f"str{opc}", f"mapped_column(String({_max(c)}){sfx})"
    if t == "cpf_cnpj":
        return f"str{opc}", f"mapped_column(String(14){sfx})"
    if t == "enum":
        return f"str{opc}", f"mapped_column(String(30){sfx})"
    if t == "texto_longo":
        return f"str{opc}", f"mapped_column(Text{sfx})"
    if t == "inteiro":
        return f"int{opc}", f"mapped_column(Integer{sfx})"
    if t == "decimal":
        return f"Decimal{opc}", f"mapped_column(Numeric(14, 2){sfx})"
    if t == "data":
        return f"date{opc}", f"mapped_column(Date{sfx})"
    if t == "booleano":
        return f"bool{opc}", f"mapped_column(Boolean{sfx})"
    return f"int{opc}", f'mapped_column(ForeignKey("{c["alvo"]}.id"){sfx})'


def gerar_models(s: dict) -> str:
    L = [f'"""{s["modulo"]} — {s["rotulo"]}: modelo de dados (gerado pela fábrica; revise e evolua)."""',
         "from __future__ import annotations", "",
         "from datetime import date, datetime  # noqa: F401",
         "from decimal import Decimal  # noqa: F401", "",
         "from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text  # noqa: F401",
         "from sqlalchemy.orm import Mapped, mapped_column", "",
         "from app.db import Base", "from app.models import utcnow", "", "",
         f"class {s['entidade']}(Base):", f'    __tablename__ = "{s["tabela"]}"',
         "    id: Mapped[int] = mapped_column(Integer, primary_key=True)"]
    for c in s["campos"]:
        anot, expr = _coluna_sa(c)
        coment = "  # dado pessoal (LGPD)" if c.get("pessoal") else ""
        L.append(f"    {c['nome']}: Mapped[{anot}] = {expr}{coment}")
    L += ["    ativo: Mapped[bool] = mapped_column(Boolean, default=True)",
          "    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)",
          "    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)", ""]
    return "\n".join(L)


def _tipo_py(c: dict, opcional: bool) -> str:
    t = c["tipo"]
    base = {"texto": "str", "texto_longo": "str", "email": "str", "cpf_cnpj": "str", "inteiro": "int", "decimal": "Decimal",
            "data": "date", "booleano": "bool", "referencia": "int"}.get(t)
    if t == "enum":
        base = "Literal[" + ", ".join(repr(o) for o in c["opcoes"]) + "]"
    return f"{base} | None" if opcional else base


def _field(c: dict, opcional: bool) -> str:
    args = ["default=None"] if opcional else []
    t = c["tipo"]
    if t in ("texto", "texto_longo", "email"):
        if c.get("obrigatorio") and not opcional:
            args.append("min_length=1")
        args.append(f"max_length={_max(c)}")
    if t == "email":
        args.append(r'pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"')
    if t in ("inteiro", "decimal"):
        if c.get("min") is not None:
            args.append(f"ge={c['min']}")
        if c.get("max") is not None:
            args.append(f"le={c['max']}")
    if t == "decimal":
        args += ["max_digits=14", "decimal_places=2"]
    if t == "referencia":
        args.append("gt=0")
    return f"Field({', '.join(args)})" if args else ""


def gerar_schemas(s: dict) -> str:
    E = s["entidade"]
    textos = [c["nome"] for c in s["campos"] if c["tipo"] in ("texto", "texto_longo")]
    cpfs = [c["nome"] for c in s["campos"] if c["tipo"] == "cpf_cnpj"]
    L = [f'"""{s["modulo"]} — {s["rotulo"]}: esquemas de entrada e saída (validação)."""',
         "from __future__ import annotations", "",
         "from datetime import date, datetime  # noqa: F401", "from decimal import Decimal  # noqa: F401",
         "from typing import Literal  # noqa: F401", "",
         "from pydantic import BaseModel, ConfigDict, Field, field_validator  # noqa: F401", "",
         "from app.modulos.validadores import validar_cpf_cnpj  # noqa: F401", "", ""]

    def validadores() -> list[str]:
        V = []
        if textos:
            V += [f"    @field_validator({', '.join(repr(t) for t in textos)})", "    @classmethod",
                  "    def _sem_espacos(cls, v):", "        if v is None:", "            return v", "        v = v.strip()",
                  "        return v", ""]
        if cpfs:
            V += [f"    @field_validator({', '.join(repr(t) for t in cpfs)})", "    @classmethod",
                  "    def _cpf_cnpj(cls, v):", "        return v if v is None else validar_cpf_cnpj(v)", ""]
        return V

    L.append(f"class {E}In(BaseModel):")
    for c in s["campos"]:
        opc = not c.get("obrigatorio")
        f = _field(c, opc)
        L.append(f"    {c['nome']}: {_tipo_py(c, opc)}" + (f" = {f}" if f else (" = None" if opc else "")))
    obrig_txt = [c["nome"] for c in s["campos"] if c["tipo"] in ("texto", "texto_longo") and c.get("obrigatorio")]
    L += [""] + validadores()
    if obrig_txt:
        L += [f"    @field_validator({', '.join(repr(t) for t in obrig_txt)})", "    @classmethod",
              "    def _obrigatorio(cls, v):", "        if not v:", '            raise ValueError("campo obrigatório")', "        return v", ""]
    L += ["", f"class {E}Update(BaseModel):"]
    for c in s["campos"]:
        f = _field(c, True)
        L.append(f"    {c['nome']}: {_tipo_py(c, True)} = {f or 'None'}")
    L += [""] + validadores()
    if obrig_txt:
        L += [f"    @field_validator({', '.join(repr(t) for t in obrig_txt)})", "    @classmethod",
              "    def _nao_vazio(cls, v):", "        if v is not None and not v:", '            raise ValueError("campo obrigatório")',
              "        return v", ""]
    L += ["", f"class {E}Out(BaseModel):", "    model_config = ConfigDict(from_attributes=True)", "    id: int"]
    for c in s["campos"]:
        L.append(f"    {c['nome']}: {_tipo_py({**c, 'tipo': 'texto' if c['tipo'] == 'enum' else c['tipo']}, not c.get('obrigatorio'))}")
    L += ["    ativo: bool", "    criado_em: datetime", "    atualizado_em: datetime", "", "",
          f"class Pagina{E}(BaseModel):", "    total: int", "    pagina: int", "    por_pagina: int", f"    itens: list[{E}Out]", ""]
    return "\n".join(L)


def gerar_router(s: dict) -> str:
    E, tab, p = s["entidade"], s["tabela"], s["permissoes"]
    busca = [c["nome"] for c in s["campos"] if c.get("busca") and c["tipo"] in ("texto", "email", "cpf_cnpj", "enum", "texto_longo")]
    unicos = [c["nome"] for c in s["campos"] if c.get("unico")]
    refs = [(c["nome"], c["alvo"]) for c in s["campos"] if c["tipo"] == "referencia"]
    pessoais = [c["nome"] for c in s["campos"] if c.get("pessoal")]
    L = [f'"""{s["modulo"]} — {s["rotulo"]}: API REST (listar, detalhar, criar, alterar, excluir logicamente)."""',
         "from __future__ import annotations", "",
         "from fastapi import APIRouter, Depends, HTTPException, Query, Request",
         "from sqlalchemy import func, or_, select, text  # noqa: F401", "from sqlalchemy.orm import Session", "",
         "from app.audit import registrar", "from app.db import get_db", "from app.deps import exigir_perfil", "from app.models import Usuario", "",
         f"from .models import {E}", f"from .schemas import {E}In, {E}Out, {E}Update, Pagina{E}", "",
         f'router = APIRouter(prefix="/api/{tab}", tags=["{s["rotulo"]}"])',
         f"LER = {tuple(p['ler'])!r}", f"ESCREVER = {tuple(p['escrever'])!r}", f"EXCLUIR = {tuple(p['excluir'])!r}",
         f"CAMPOS_PESSOAIS = {set(pessoais) or 'set()'!s}  # não vão para os detalhes da auditoria (LGPD)",
         f"UNICOS = {unicos!r}", f"REFERENCIAS = {dict(refs)!r}", "", "",
         "def _escapar(t: str) -> str:", r'    return t.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")', "", "",
         "def _auditavel(d: dict) -> dict:", "    return {k: ('***' if k in CAMPOS_PESSOAIS else v) for k, v in d.items()}", "", "",
         f"def _obter(db: Session, rid: int) -> {E}:", f"    obj = db.get({E}, rid)", "    if not obj:",
         f'        raise HTTPException(404, "{s["rotulo"]}: registro não encontrado")', "    return obj", "", "",
         f"def _validar(db: Session, dados: dict, rid: int | None = None) -> None:",
         "    for campo in UNICOS:", "        if dados.get(campo) is not None:",
         f"            q = select({E}.id).where(getattr({E}, campo) == dados[campo])",
         f"            if rid:", f"                q = q.where({E}.id != rid)",
         "            if db.scalar(q):", '                raise HTTPException(409, f"Já existe registro com este {campo}")',
         "    for campo, alvo in REFERENCIAS.items():", "        if dados.get(campo) is not None:",
         '            if not db.execute(text(f"SELECT 1 FROM {alvo} WHERE id = :i"), {"i": dados[campo]}).first():',
         '                raise HTTPException(422, f"{campo}: registro relacionado não existe")', "", "",
         f'@router.get("", response_model=Pagina{E})',
         'def listar(q: str = Query("", max_length=200), pagina: int = Query(1, ge=1), por_pagina: int = Query(20, ge=1, le=100),',
         "           incluir_inativos: bool = False, db: Session = Depends(get_db), _: Usuario = Depends(exigir_perfil(*LER))):",
         f"    consulta = select({E})", "    if not incluir_inativos:", f"        consulta = consulta.where({E}.ativo.is_(True))"]
    if busca:
        L += ["    for termo in q.split():", '        padrao = f"%{_escapar(termo.lower())}%"',
              "        consulta = consulta.where(or_(" + ", ".join(f'func.lower({E}.{b}).like(padrao, escape="\\\\")' for b in busca) + "))"]
    L += ["    total = db.scalar(select(func.count()).select_from(consulta.subquery()))",
          f"    itens = db.scalars(consulta.order_by({E}.id.desc()).offset((pagina - 1) * por_pagina).limit(por_pagina)).all()",
          '    return {"total": total, "pagina": pagina, "por_pagina": por_pagina, "itens": itens}', "", "",
          f'@router.get("/{{rid}}", response_model={E}Out)',
          "def detalhar(rid: int, db: Session = Depends(get_db), _: Usuario = Depends(exigir_perfil(*LER))):",
          "    return _obter(db, rid)", "", "",
          f'@router.post("", response_model={E}Out, status_code=201)',
          f"def criar(dados: {E}In, request: Request, db: Session = Depends(get_db), u: Usuario = Depends(exigir_perfil(*ESCREVER))):",
          "    d = dados.model_dump()", "    _validar(db, d)", f"    obj = {E}(**d)", "    db.add(obj)", "    db.flush()",
          f'    registrar(db, acao="{tab.upper()}_CRIADO", recurso="{tab}", recurso_id=obj.id, usuario=u, request=request,',
          "              detalhes=_auditavel(d), commit=False)", "    db.commit()", "    db.refresh(obj)", "    return obj", "", "",
          f'@router.patch("/{{rid}}", response_model={E}Out)',
          f"def alterar(rid: int, dados: {E}Update, request: Request, db: Session = Depends(get_db),",
          "            u: Usuario = Depends(exigir_perfil(*ESCREVER))):",
          "    obj = _obter(db, rid)", "    mud = dados.model_dump(exclude_unset=True, exclude_none=True)", "    _validar(db, mud, rid)",
          "    antes = {k: getattr(obj, k) for k in mud}", "    for k, v in mud.items():", "        setattr(obj, k, v)",
          f'    registrar(db, acao="{tab.upper()}_ALTERADO", recurso="{tab}", recurso_id=obj.id, usuario=u, request=request,',
          '              detalhes={"antes": _auditavel(antes), "depois": _auditavel(mud)}, commit=False)',
          "    db.commit()", "    db.refresh(obj)", "    return obj", "", "",
          '@router.delete("/{rid}", status_code=204)',
          "def excluir(rid: int, request: Request, db: Session = Depends(get_db), u: Usuario = Depends(exigir_perfil(*EXCLUIR))):",
          '    """Exclusão lógica: o registro fica inativo e continua na base (rastreabilidade)."""',
          "    obj = _obter(db, rid)", "    obj.ativo = False",
          f'    registrar(db, acao="{tab.upper()}_EXCLUIDO", recurso="{tab}", recurso_id=obj.id, usuario=u, request=request)', ""]
    return "\n".join(L)


def _sa_tipo_mig(c: dict) -> str:
    t = c["tipo"]
    return {"texto": f"sa.String({_max(c)})", "email": f"sa.String({_max(c)})", "cpf_cnpj": "sa.String(14)", "enum": "sa.String(30)",
            "texto_longo": "sa.Text()", "inteiro": "sa.Integer()", "decimal": "sa.Numeric(14, 2)", "data": "sa.Date()",
            "booleano": "sa.Boolean()", "referencia": "sa.Integer()"}[t]


def cabeca_alembic(versoes: Path) -> tuple[str | None, int]:
    revs, downs = {}, set()
    for f in versoes.glob("*.py"):
        t = f.read_text(encoding="utf-8")
        r = re.search(r'^revision\s*=\s*"([^"]+)"', t, re.M)
        d = re.search(r'^down_revision\s*=\s*(?:"([^"]+)"|None)', t, re.M)
        if r:
            revs[r.group(1)] = f
            if d and d.group(1):
                downs.add(d.group(1))
    cabecas = [r for r in revs if r not in downs]
    if len(cabecas) > 1:
        raise ErroGerador(f"migrações com mais de uma cabeça: {cabecas}")
    return (cabecas[0] if cabecas else None), len(revs)


def gerar_migracao(s: dict, versoes: Path) -> tuple[str, str]:
    cabeca, n = cabeca_alembic(versoes)
    rev = f"{n + 1:04d}_{s['tabela']}"[:32]
    tab = s["tabela"]
    L = [f'"""{s["modulo"]} — cria a tabela {tab} ({s["rotulo"]}).', "", f"Revision ID: {rev}", f"Revises: {cabeca}", '"""',
         "import sqlalchemy as sa", "from alembic import op", "", f'revision = "{rev}"',
         f"down_revision = {cabeca!r}".replace("'", '"'), "branch_labels = None", "depends_on = None", "", "",
         "def upgrade() -> None:", "    op.create_table(", f'        "{tab}",', '        sa.Column("id", sa.Integer(), primary_key=True),']
    for c in s["campos"]:
        fk = f', sa.ForeignKey("{c["alvo"]}.id")' if c["tipo"] == "referencia" else ""
        L.append(f'        sa.Column("{c["nome"]}", {_sa_tipo_mig(c)}{fk}, nullable={not c.get("obrigatorio")}),')
    L += ['        sa.Column("ativo", sa.Boolean(), nullable=False),',
          '        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),',
          '        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),', "    )"]
    for c in s["campos"]:
        if c.get("unico") or c.get("busca") or c["tipo"] == "referencia":
            L.append(f'    op.create_index("ix_{tab}_{c["nome"]}", "{tab}", ["{c["nome"]}"], unique={bool(c.get("unico"))})')
    L += ["", "", "def downgrade() -> None:", f'    op.drop_table("{tab}")', ""]
    return rev, "\n".join(L)


# ----------------------------------------------------------------- testes de API

def _valor(c: dict, i: int = 0):
    t = c["tipo"]
    if t in ("texto", "texto_longo"):
        return f"{_rotulo_campo(c)} de teste {i}"[: _max(c)]
    if t == "email":
        return f"pessoa{i}@exemplo.gov.br"
    if t == "cpf_cnpj":
        return CPFS_VALIDOS[i % len(CPFS_VALIDOS)]
    if t == "enum":
        return c["opcoes"][i % len(c["opcoes"])]
    if t == "inteiro":
        return int(c.get("min") or 0) + 1 + i
    if t == "decimal":
        return f"{(float(c.get('min') or 0) + 10.5 + i):.2f}"
    if t == "data":
        return f"2026-01-{10 + i:02d}"
    if t == "booleano":
        return True
    return None  # referencia: preenchida em tempo de teste


def gerar_testes(s: dict, specs: dict[str, dict]) -> str:
    tab, E = s["tabela"], s["entidade"]
    refs = [c for c in s["campos"] if c["tipo"] == "referencia"]
    pode_escrever = s["permissoes"]["escrever"][0]
    sem_escrita = [p for p in PERFIS if p not in s["permissoes"]["escrever"] and p in s["permissoes"]["ler"]]
    L = [f'"""{s["modulo"]} — testes da API de {s["rotulo"]} (gerados pela fábrica)."""', "",
         f'URL = "/api/{tab}"', f'ESCRITA = "{pode_escrever}"', f'EXCLUSAO = "{s["permissoes"]["excluir"][0]}"', ""]
    # helpers para referências
    for c in refs:
        alvo = specs.get(c["alvo"])
        if not alvo:
            raise ErroGerador(f"especificação do alvo '{c['alvo']}' não encontrada (gere o alvo antes)")
        corpo = {k["nome"]: _valor(k, 3) for k in alvo["campos"] if k.get("obrigatorio") and k["tipo"] != "referencia"}
        L += [f"def criar_{c['alvo']}(client, h, i=3):",
              f"    corpo = {corpo!r}"]
        for k in alvo["campos"]:
            if k.get("unico") and k.get("obrigatorio"):
                if k["tipo"] == "cpf_cnpj":
                    L.append(f'    corpo["{k["nome"]}"] = {CPFS_VALIDOS!r}[i % {len(CPFS_VALIDOS)}]')
                elif k["tipo"] in ("texto", "email"):
                    L.append(f'    corpo["{k["nome"]}"] = f"{{i}}-" + str(corpo["{k["nome"]}"])')
        L += [f'    r = client.post("/api/{c["alvo"]}", json=corpo, headers=h)', "    assert r.status_code == 201, r.text",
              '    return r.json()["id"]', "", ""]
    obrig = {c["nome"]: _valor(c, 0) for c in s["campos"] if c.get("obrigatorio") and c["tipo"] != "referencia"}
    completo = {c["nome"]: _valor(c, 0) for c in s["campos"] if c["tipo"] != "referencia"}
    L += ["def payload(client, h, i=0, completo=False):",
          f"    corpo = dict({completo!r}) if completo else dict({obrig!r})"]
    for c in s["campos"]:
        if c.get("unico") and c["tipo"] != "referencia":
            if c["tipo"] == "cpf_cnpj":
                L.append(f'    corpo["{c["nome"]}"] = {CPFS_VALIDOS!r}[i % {len(CPFS_VALIDOS)}]')
            elif c["tipo"] in ("texto", "email"):
                L.append(f'    corpo["{c["nome"]}"] = f"{{i}}-" + str(corpo["{c["nome"]}"])')
            elif c["tipo"] == "inteiro":
                L.append(f'    corpo["{c["nome"]}"] = corpo["{c["nome"]}"] + i')
    for c in refs:
        if c.get("obrigatorio"):
            L.append(f'    corpo["{c["nome"]}"] = criar_{c["alvo"]}(client, h, i + 3)')
    L += ["    return corpo", "", "",
          "def test_criar_e_detalhar(client, usuarios):", "    h = usuarios[ESCRITA]", "    corpo = payload(client, h, completo=True)",
          "    r = client.post(URL, json=corpo, headers=h)", "    assert r.status_code == 201, r.text", "    obj = r.json()",
          "    assert obj['ativo'] is True and obj['id'] > 0",
          "    d = client.get(f\"{URL}/{obj['id']}\", headers=h).json()", "    for k, v in corpo.items():",
          "        assert str(d[k]) == str(v), k", "", "",
          "def test_listar_paginado(client, usuarios):", "    h = usuarios[ESCRITA]", "    for i in range(3):",
          "        assert client.post(URL, json=payload(client, h, i), headers=h).status_code == 201",
          "    r = client.get(URL, params={'por_pagina': 2, 'pagina': 2}, headers=h).json()",
          "    assert r['total'] == 3 and len(r['itens']) == 1",
          "    assert client.get(URL, params={'por_pagina': 1000}, headers=h).status_code == 422", "", ""]
    busca = [c for c in s["campos"] if c.get("busca") and c["tipo"] in ("texto", "email")]
    if busca:
        b = busca[0]["nome"]
        L += ["def test_busca_por_texto(client, usuarios):", "    h = usuarios[ESCRITA]",
              "    a = payload(client, h, 0)", "    client.post(URL, json=a, headers=h)",
              "    client.post(URL, json=payload(client, h, 1), headers=h)",
              f"    termo = str(a['{b}']).split()[0]",
              "    itens = client.get(URL, params={'q': termo}, headers=h).json()['itens']",
              f"    assert itens and all(termo.lower() in str(x['{b}']).lower() for x in itens)",
              "    assert client.get(URL, params={'q': 'inexistente-xyz'}, headers=h).json()['total'] == 0", "", ""]
    altera = next((c for c in s["campos"] if c["tipo"] in ("texto", "texto_longo") and not c.get("unico")), None)
    if altera:
        L += ["def test_alterar(client, usuarios):", "    h = usuarios[ESCRITA]",
              "    obj = client.post(URL, json=payload(client, h), headers=h).json()",
              f"    r = client.patch(f\"{{URL}}/{{obj['id']}}\", json={{'{altera['nome']}': 'Valor alterado'}}, headers=h)",
              f"    assert r.status_code == 200 and r.json()['{altera['nome']}'] == 'Valor alterado'", "", ""]
    L += ["def test_excluir_logicamente(client, usuarios):", "    h = usuarios[EXCLUSAO]",
          "    obj = client.post(URL, json=payload(client, usuarios[ESCRITA]), headers=usuarios[ESCRITA]).json()",
          "    assert client.delete(f\"{URL}/{obj['id']}\", headers=h).status_code == 204",
          "    assert client.get(URL, headers=h).json()['total'] == 0",
          "    assert client.get(URL, params={'incluir_inativos': True}, headers=h).json()['total'] == 1",
          "    assert client.get(f\"{URL}/{obj['id']}\", headers=h).json()['ativo'] is False", "", "",
          "def test_obrigatorios(client, usuarios):",
          "    assert client.post(URL, json={}, headers=usuarios[ESCRITA]).status_code == 422", "", "",
          "def test_inexistente(client, usuarios):",
          "    assert client.get(f'{URL}/999999', headers=usuarios[ESCRITA]).status_code == 404", "", "",
          "def test_auditoria_registrada(client, usuarios):", "    h = usuarios[ESCRITA]",
          "    obj = client.post(URL, json=payload(client, h), headers=h).json()",
          f"    acoes = client.get('/api/auditoria', params={{'recurso': '{tab}'}}, headers=usuarios['ADMIN']).json()['itens']",
          f"    assert any(a['acao'] == '{tab.upper()}_CRIADO' and a['recurso_id'] == str(obj['id']) for a in acoes)", ""]
    for c in s["campos"]:
        if c.get("pessoal"):
            L += [f"    det = next(a for a in acoes if a['acao'] == '{tab.upper()}_CRIADO')['detalhes']",
                  f"    assert '\"{c['nome']}\": \"***\"' in det  # LGPD: dado pessoal não vai para a auditoria", ""]
            break
    L.append("")
    if sem_escrita:
        L += ["def test_permissao_de_escrita(client, usuarios):",
              f"    assert client.post(URL, json=payload(client, usuarios[ESCRITA]), headers=usuarios['{sem_escrita[0]}']).status_code == 403", "", ""]
    for c in s["campos"]:
        if c["tipo"] in ("texto", "email") and c.get("max"):
            L += [f"def test_tamanho_maximo_{c['nome']}(client, usuarios):", "    h = usuarios[ESCRITA]",
                  f"    corpo = payload(client, h); corpo['{c['nome']}'] = 'x' * {_max(c) + 1}",
                  "    assert client.post(URL, json=corpo, headers=h).status_code == 422", "", ""]
        if c["tipo"] == "enum":
            L += [f"def test_enum_invalido_{c['nome']}(client, usuarios):", "    h = usuarios[ESCRITA]",
                  f"    corpo = payload(client, h); corpo['{c['nome']}'] = 'OPCAO_INEXISTENTE'",
                  "    assert client.post(URL, json=corpo, headers=h).status_code == 422", "", ""]
        if c["tipo"] == "cpf_cnpj":
            L += [f"def test_cpf_cnpj_invalido_{c['nome']}(client, usuarios):", "    h = usuarios[ESCRITA]",
                  f"    corpo = payload(client, h); corpo['{c['nome']}'] = '111.111.111-11'",
                  "    assert client.post(URL, json=corpo, headers=h).status_code == 422", "", ""]
        if c.get("unico"):
            L += [f"def test_unico_{c['nome']}(client, usuarios):", "    h = usuarios[ESCRITA]", "    corpo = payload(client, h)",
                  "    assert client.post(URL, json=corpo, headers=h).status_code == 201",
                  "    outro = payload(client, h, 1)", f"    outro['{c['nome']}'] = corpo['{c['nome']}']",
                  "    assert client.post(URL, json=outro, headers=h).status_code == 409", "", ""]
        if c["tipo"] == "referencia":
            L += [f"def test_referencia_inexistente_{c['nome']}(client, usuarios):", "    h = usuarios[ESCRITA]",
                  f"    corpo = payload(client, h); corpo['{c['nome']}'] = 999999",
                  "    assert client.post(URL, json=corpo, headers=h).status_code == 422", "", ""]
    return "\n".join(L).rstrip() + "\n"


# ----------------------------------------------------------------- frontend

def _ts_tipo(c: dict) -> str:
    t = c["tipo"]
    if t == "enum":
        base = " | ".join(f'"{o}"' for o in c["opcoes"])
    else:
        base = {"inteiro": "number", "referencia": "number", "booleano": "boolean"}.get(t, "string")
    return base if c.get("obrigatorio") else f"{base} | null"


def gerar_api_ts(s: dict) -> str:
    E, tab = s["entidade"], s["tabela"]
    L = [f"// {s['modulo']} — {s['rotulo']}: cliente da API (gerado pela fábrica).",
         'import { api, json, qs, type Pagina } from "../../api/client";', "",
         f"export interface {E} {{", "  id: number;"]
    L += [f"  {c['nome']}: {_ts_tipo(c)};" for c in s["campos"]]
    L += ["  ativo: boolean;", "  criado_em: string;", "  atualizado_em: string;", "}", "",
          f"export type {E}Dados = Omit<{E}, \"id\" | \"ativo\" | \"criado_em\" | \"atualizado_em\">;", "",
          f"export const listar{E} = (q = \"\", pagina = 1) => api<Pagina<{E}>>(`/api/{tab}${{qs({{ q, pagina, por_pagina: 20 }})}}`);",
          f"export const criar{E} = (d: {E}Dados) => api<{E}>(\"/api/{tab}\", {{ method: \"POST\", body: json(d) }});",
          f"export const alterar{E} = (id: number, d: Partial<{E}Dados>) => api<{E}>(`/api/{tab}/${{id}}`, {{ method: \"PATCH\", body: json(d) }});",
          f"export const excluir{E} = (id: number) => api<void>(`/api/{tab}/${{id}}`, {{ method: \"DELETE\" }});", ""]
    return "\n".join(L)


def gerar_pagina_tsx(s: dict, specs: dict[str, dict]) -> str:
    E, tab, p = s["entidade"], s["tabela"], s["permissoes"]
    refs = [c for c in s["campos"] if c["tipo"] == "referencia"]
    cols = [c for c in s["campos"] if c["tipo"] not in ("texto_longo",)][:6]
    vazio = []
    for c in s["campos"]:
        v = {"booleano": "false", "inteiro": "null", "referencia": "null"}.get(c["tipo"], '""')
        if c["tipo"] == "enum":
            v = f'"{c["opcoes"][0]}"' if c.get("obrigatorio") else '""'
        vazio.append(f"{c['nome']}: {v}")
    L = [f"// {s['modulo']} — {s['rotulo']}: lista, busca, cadastro, edição e exclusão (gerado pela fábrica).",
         'import { useCallback, useEffect, useState } from "react";',
         ('import { api, qs, type Pagina } from "../../api/client";' if refs else 'import type { Pagina } from "../../api/client";'),
         'import { useAuth } from "../../auth";', 'import { Alerta } from "../../components/Alerta";',
         'import { Paginacao } from "../../components/Paginacao";',
         f'import {{ alterar{E}, criar{E}, excluir{E}, listar{E}, type {E}, type {E}Dados }} from "./api";', "",
         f"const ESCREVER = {p['escrever']!r};".replace("'", '"'), f"const EXCLUIR = {p['excluir']!r};".replace("'", '"'),
         f"type Form = Record<keyof {E}Dados, unknown>;",
         f"const VAZIO: Form = {{ {', '.join(vazio)} }};", "",
         f"export function validar{E}(d: Form): string | null {{"]
    for c in s["campos"]:
        if c.get("obrigatorio") and c["tipo"] != "booleano":
            L.append(f'  if (d.{c["nome"]} === "" || d.{c["nome"]} === null || d.{c["nome"]} === undefined) return "{_rotulo_campo(c)} é obrigatório";')
        if c["tipo"] in ("texto", "email", "texto_longo"):
            L.append(f'  if (typeof d.{c["nome"]} === "string" && d.{c["nome"]}.length > {_max(c)}) return "{_rotulo_campo(c)}: máximo de {_max(c)} caracteres";')
        if c["tipo"] == "email":
            L.append(f'  if (d.{c["nome"]} && !/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(String(d.{c["nome"]}))) return "{_rotulo_campo(c)}: e-mail inválido";')
    L += ["  return null;", "}", "",
          f"function paraEnvio(d: Form): {E}Dados {{",
          "  const saida: Record<string, unknown> = {};",
          "  for (const [k, v] of Object.entries(d)) saida[k] = v === \"\" ? null : v;",
          f"  return saida as unknown as {E}Dados;", "}", "",
          f"export function {E}Pagina() {{", "  const { usuario } = useAuth();",
          "  const podeEscrever = !!usuario && ESCREVER.includes(usuario.perfil);",
          "  const podeExcluir = !!usuario && EXCLUIR.includes(usuario.perfil);",
          f"  const [res, setRes] = useState<Pagina<{E}> | null>(null);",
          '  const [q, setQ] = useState("");', "  const [pagina, setPagina] = useState(1);",
          "  const [form, setForm] = useState<Form | null>(null);", "  const [editando, setEditando] = useState<number | null>(null);",
          '  const [erro, setErro] = useState("");', '  const [ok, setOk] = useState("");']
    for c in refs:
        L.append(f"  const [op_{c['nome']}, setOp_{c['nome']}] = useState<{{ id: number; rotulo: string }}[]>([]);")
    L += ["", f"  const carregar = useCallback(() => {{ listar{E}(q, pagina).then(setRes).catch((e) => setErro(e.message)); }}, [q, pagina]);",
          "  useEffect(carregar, [carregar]);"]
    for c in refs:
        alvo = specs.get(c["alvo"], {})
        rot = next((k["nome"] for k in alvo.get("campos", []) if k["tipo"] in ("texto", "email")), "id")
        L.append(f"  useEffect(() => {{ api<Pagina<Record<string, unknown>>>(`/api/{c['alvo']}${{qs({{ por_pagina: 100 }})}}`)"
                 f".then((p) => setOp_{c['nome']}(p.itens.map((x) => ({{ id: Number(x.id), rotulo: String(x.{rot}) }})))).catch(() => {{}}); }}, []);")
    L += ["", "  async function salvar(e: React.FormEvent) {", '    e.preventDefault(); setErro(""); setOk("");',
          "    if (!form) return;", f"    const problema = validar{E}(form);", "    if (problema) { setErro(problema); return; }",
          "    try {", f"      if (editando) await alterar{E}(editando, paraEnvio(form)); else await criar{E}(paraEnvio(form));",
          '      setOk("Salvo com sucesso."); setForm(null); setEditando(null); carregar();',
          "    } catch (err) { setErro((err as Error).message); }", "  }", "",
          f"  async function excluir(item: {E}) {{",
          f'    if (!window.confirm("Excluir este registro? Ele ficará inativo.")) return;',
          f'    try {{ await excluir{E}(item.id); setOk("Registro excluído."); carregar(); }} catch (err) {{ setErro((err as Error).message); }}', "  }", "",
          "  const set = (k: string, v: unknown) => setForm((f) => ({ ...(f as Form), [k]: v }));", "",
          "  return (", "    <section>", '      <div className="cabecalho-secao">', f"        <h1>{s['rotulo']}</h1>",
          '        {podeEscrever && !form && <button type="button" onClick={() => { setForm({ ...VAZIO }); setEditando(null); }}>Novo</button>}',
          "      </div>",
          '      <form role="search" className="form-grade" onSubmit={(e) => { e.preventDefault(); setPagina(1); carregar(); }}>',
          f'        <div className="largo"><label htmlFor="busca-{tab}">Pesquisar</label>',
          f'          <input id="busca-{tab}" type="search" value={{q}} onChange={{(e) => setQ(e.target.value)}} maxLength={{200}} /></div>',
          "      </form>",
          "      {form && (",
          f'        <form onSubmit={{salvar}} className="form-grade" aria-label="Dados de {s["rotulo"]}">']
    for c in s["campos"]:
        fid = f"{tab}-{c['nome']}"
        rot = _rotulo_campo(c) + (" *" if c.get("obrigatorio") else "")
        val = f"(form.{c['nome']} ?? \"\") as string"
        t = c["tipo"]
        if t == "texto_longo":
            campo = f'<textarea id="{fid}" rows={{3}} value={{{val}}} onChange={{(e) => set("{c["nome"]}", e.target.value)}} />'
        elif t == "booleano":
            campo = f'<input id="{fid}" type="checkbox" checked={{!!form.{c["nome"]}}} onChange={{(e) => set("{c["nome"]}", e.target.checked)}} />'
        elif t == "enum":
            ops = "".join(f'<option value="{o}">{o}</option>' for o in c["opcoes"])
            campo = f'<select id="{fid}" value={{{val}}} onChange={{(e) => set("{c["nome"]}", e.target.value)}}>' + ('<option value="">—</option>' if not c.get("obrigatorio") else "") + ops + "</select>"
        elif t == "referencia":
            campo = (f'<select id="{fid}" value={{String(form.{c["nome"]} ?? "")}} onChange={{(e) => set("{c["nome"]}", e.target.value ? Number(e.target.value) : null)}}>'
                     f'<option value="">Selecione…</option>{{op_{c["nome"]}.map((o) => <option key={{o.id}} value={{o.id}}>{{o.rotulo}}</option>)}}</select>')
        elif t in ("inteiro", "decimal"):
            passo = ' step="0.01"' if t == "decimal" else ""
            conv = 'e.target.value === "" ? null : Number(e.target.value)' if t == "inteiro" else "e.target.value"
            campo = f'<input id="{fid}" type="number"{passo} value={{{val}}} onChange={{(e) => set("{c["nome"]}", {conv})}} />'
        else:
            tipo_html = {"email": "email", "data": "date"}.get(t, "text")
            mx = f" maxLength={{{_max(c)}}}" if t in ("texto", "email") else ""
            campo = f'<input id="{fid}" type="{tipo_html}"{mx} value={{{val}}} onChange={{(e) => set("{c["nome"]}", e.target.value)}} />'
        largo = ' className="largo"' if t == "texto_longo" else ""
        L.append(f'          <div{largo}><label htmlFor="{fid}">{rot}</label>{campo}</div>')
    L += ['          <div className="largo"><button type="submit">{editando ? "Salvar alterações" : "Cadastrar"}</button>',
          '            {" "}<button type="button" onClick={() => { setForm(null); setEditando(null); }}>Cancelar</button></div>',
          "        </form>", "      )}", "      <Alerta>{erro}</Alerta>", '      <Alerta tipo="sucesso">{ok}</Alerta>',
          "      {res && (<>", '        <div className="tabela-rolagem"><table>',
          f'          <caption className="sr-only">{s["rotulo"]}</caption>',
          "          <thead><tr>" + "".join(f'<th scope="col">{_rotulo_campo(c)}</th>' for c in cols) + '<th scope="col">Ações</th></tr></thead>',
          "          <tbody>{res.itens.map((x) => (", "            <tr key={x.id}>"
          + "".join((f"<td>{{op_{c['nome']}.find((o) => o.id === x.{c['nome']})?.rotulo ?? String(x.{c['nome']} ?? \"—\")}}</td>"
                     if c["tipo"] == "referencia" else f"<td>{{String(x.{c['nome']} ?? \"—\")}}</td>") for c in cols)
          + "<td>{podeEscrever && <button type=\"button\" onClick={() => { const { id, ativo, criado_em, atualizado_em, ...d } = x; void id; void ativo; void criado_em; void atualizado_em; setForm(d as Form); setEditando(x.id); }}>Editar</button>}"
          + "{\" \"}{podeExcluir && <button type=\"button\" onClick={() => excluir(x)}>Excluir</button>}</td></tr>",
          "          ))}</tbody>", "        </table></div>",
          '        {res.itens.length === 0 && <p className="vazio">Nenhum registro.</p>}',
          "        <Paginacao pagina={res.pagina} total={res.total} porPagina={res.por_pagina} aoMudar={setPagina} />",
          "      </>)}", "    </section>", "  );", "}", ""]
    return "\n".join(L)


def gerar_teste_tsx(s: dict) -> str:
    E, tab = s["entidade"], s["tabela"]
    item = {"id": 1, "ativo": True, "criado_em": "2026-01-01T00:00:00Z", "atualizado_em": "2026-01-01T00:00:00Z"}
    for c in s["campos"]:
        v = _valor(c, 0)
        item[c["nome"]] = 1 if c["tipo"] == "referencia" else v
    primeiro = next(c for c in s["campos"] if c["tipo"] not in ("texto_longo",))
    obrig = next((c for c in s["campos"] if c.get("obrigatorio") and c["tipo"] in ("texto", "email", "texto_longo", "cpf_cnpj")), None)
    import json as _json
    L = [f"// {s['modulo']} — testes da tela de {s['rotulo']} (gerados pela fábrica).",
         'import { render, screen } from "@testing-library/react";', 'import userEvent from "@testing-library/user-event";',
         'import { MemoryRouter } from "react-router-dom";', 'import { afterEach, expect, it, vi } from "vitest";',
         'import { AuthProvider } from "../../auth";', f'import {{ {E}Pagina, validar{E} }} from "./{E}Pagina";', "",
         "afterEach(() => vi.restoreAllMocks());", "",
         f"const ITEM = {_json.dumps(item, ensure_ascii=False)};", "",
         "function mockApi() {",
         "  return vi.spyOn(globalThis, \"fetch\").mockImplementation(async () => new Response(",
         "    JSON.stringify({ total: 1, pagina: 1, por_pagina: 20, itens: [ITEM] }), { status: 200, headers: { \"content-type\": \"application/json\" } }));",
         "}", "",
         "it(\"lista os registros vindos da API\", async () => {", "  mockApi();",
         f"  render(<MemoryRouter><AuthProvider><{E}Pagina /></AuthProvider></MemoryRouter>);",
         f"  expect(await screen.findByText(String(ITEM.{primeiro['nome']}))).toBeTruthy();",
         f"  expect(screen.getByRole(\"heading\", {{ name: \"{s['rotulo']}\" }})).toBeTruthy();", "});", "",
         "it(\"pesquisa envia o termo para a API\", async () => {", "  const f = mockApi();",
         f"  render(<MemoryRouter><AuthProvider><{E}Pagina /></AuthProvider></MemoryRouter>);",
         "  await userEvent.type(screen.getByRole(\"searchbox\"), \"abc{Enter}\");",
         f"  expect(f.mock.calls.some(([u]) => String(u).includes(\"/api/{tab}\") && String(u).includes(\"q=abc\"))).toBe(true);", "});", ""]
    if obrig:
        L += ["it(\"valida campo obrigatório\", () => {",
              f"  const d = {{ ...ITEM }} as Record<string, unknown>; d.{obrig['nome']} = \"\";",
              f"  expect(validar{E}(d as never)).toMatch(/obrigatório/);",
              f"  expect(validar{E}(ITEM as never)).toBeNull();", "});", ""]
    return "\n".join(L)


# ----------------------------------------------------------------- orquestração

def gerar_crud(spec_path: Path, projeto: Path) -> dict[str, list[str]]:
    """Gera todos os arquivos da entidade no projeto (backend + frontend). Retorna os caminhos por camada."""
    s = carregar_spec(spec_path)
    be, fe = projeto / "backend", projeto / "frontend"
    if not (be / "app" / "modulos" / "__init__.py").exists():
        raise ErroGerador("projeto sem base modular (backend/app/modulos/__init__.py)")
    destino_spec = projeto / "especificacoes" / f"{s['tabela']}.yaml"
    destino_spec.parent.mkdir(parents=True, exist_ok=True)
    destino_spec.write_text(spec_path.read_text(encoding="utf-8"), encoding="utf-8")
    specs = {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in (projeto / "especificacoes").glob("*.yaml")}
    pkg = be / "app" / "modulos" / s["tabela"]
    if pkg.exists():
        raise ErroGerador(f"módulo já existe: {pkg} (apague para regerar)")
    pkg.mkdir(parents=True)
    arquivos: dict[str, list[str]] = {"backend": [], "banco": [], "testes": [], "frontend": []}

    def escrever(p: Path, conteudo: str, camada: str) -> None:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(conteudo, encoding="utf-8")
        arquivos[camada].append(str(p.relative_to(projeto)))

    escrever(pkg / "__init__.py", f'"""{s["modulo"]} — {s["rotulo"]}."""\n', "backend")
    escrever(pkg / "models.py", gerar_models(s), "backend")
    escrever(pkg / "schemas.py", gerar_schemas(s), "backend")
    escrever(pkg / "router.py", gerar_router(s), "backend")
    rev, mig = gerar_migracao(s, be / "migrations" / "versions")
    escrever(be / "migrations" / "versions" / f"{rev}.py", mig, "banco")
    escrever(be / "tests" / f"test_{_mod_slug(s)}_{s['tabela']}.py", gerar_testes(s, specs), "testes")
    fdir = fe / "src" / "modulos" / s["tabela"]
    escrever(fdir / "api.ts", gerar_api_ts(s), "frontend")
    escrever(fdir / f"{s['entidade']}Pagina.tsx", gerar_pagina_tsx(s, specs), "frontend")
    escrever(fdir / f"{s['entidade']}Pagina.test.tsx", gerar_teste_tsx(s), "testes")
    app = fe / "src" / "App.tsx"
    t = app.read_text(encoding="utf-8")
    for marca in ("// fabrica:imports", "{/* fabrica:menu */}", "{/* fabrica:rotas */}"):
        if marca not in t:
            raise ErroGerador(f"App.tsx sem o marcador {marca}")
    E, tab = s["entidade"], s["tabela"]
    t = t.replace("// fabrica:imports", f'import {{ {E}Pagina }} from "./modulos/{tab}/{E}Pagina";\n// fabrica:imports')
    t = t.replace("{/* fabrica:menu */}", f'<NavLink to="/{tab}">{s["rotulo"]}</NavLink>\n          {{/* fabrica:menu */}}')
    t = t.replace("{/* fabrica:rotas */}", f'<Route path="/{tab}" element={{<{E}Pagina />}} />\n        {{/* fabrica:rotas */}}')
    app.write_text(t, encoding="utf-8")
    arquivos["frontend"].append(str(app.relative_to(projeto)))
    arquivos["especificacao"] = [str(destino_spec.relative_to(projeto))]
    return arquivos
