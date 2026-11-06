// MOD-101 — Unidades: lista, busca, cadastro, edição e exclusão (gerado pela fábrica).
import { useCallback, useEffect, useState } from "react";
import type { Pagina } from "../../api/client";
import { useAuth } from "../../auth";
import { Alerta } from "../../components/Alerta";
import { Paginacao } from "../../components/Paginacao";
import { alterarUnidade, criarUnidade, excluirUnidade, listarUnidade, type Unidade, type UnidadeDados } from "./api";

const ESCREVER = ["ADMIN", "GESTOR"];
const EXCLUIR = ["ADMIN"];
type Form = Record<keyof UnidadeDados, unknown>;
const VAZIO: Form = { nome: "", sigla: "", municipio: "", telefone: "" };

export function validarUnidade(d: Form): string | null {
  if (d.nome === "" || d.nome === null || d.nome === undefined) return "Nome é obrigatório";
  if (typeof d.nome === "string" && d.nome.length > 150) return "Nome: máximo de 150 caracteres";
  if (d.sigla === "" || d.sigla === null || d.sigla === undefined) return "Sigla é obrigatório";
  if (typeof d.sigla === "string" && d.sigla.length > 20) return "Sigla: máximo de 20 caracteres";
  if (d.municipio === "" || d.municipio === null || d.municipio === undefined) return "Município é obrigatório";
  if (typeof d.municipio === "string" && d.municipio.length > 100) return "Município: máximo de 100 caracteres";
  if (typeof d.telefone === "string" && d.telefone.length > 20) return "Telefone: máximo de 20 caracteres";
  return null;
}

function paraEnvio(d: Form): UnidadeDados {
  const saida: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(d)) saida[k] = v === "" ? null : v;
  return saida as unknown as UnidadeDados;
}

export function UnidadePagina() {
  const { usuario } = useAuth();
  const podeEscrever = !!usuario && ESCREVER.includes(usuario.perfil);
  const podeExcluir = !!usuario && EXCLUIR.includes(usuario.perfil);
  const [res, setRes] = useState<Pagina<Unidade> | null>(null);
  const [q, setQ] = useState("");
  const [pagina, setPagina] = useState(1);
  const [form, setForm] = useState<Form | null>(null);
  const [editando, setEditando] = useState<number | null>(null);
  const [erro, setErro] = useState("");
  const [ok, setOk] = useState("");

  const carregar = useCallback(() => { listarUnidade(q, pagina).then(setRes).catch((e) => setErro(e.message)); }, [q, pagina]);
  useEffect(carregar, [carregar]);

  async function salvar(e: React.FormEvent) {
    e.preventDefault(); setErro(""); setOk("");
    if (!form) return;
    const problema = validarUnidade(form);
    if (problema) { setErro(problema); return; }
    try {
      if (editando) await alterarUnidade(editando, paraEnvio(form)); else await criarUnidade(paraEnvio(form));
      setOk("Salvo com sucesso."); setForm(null); setEditando(null); carregar();
    } catch (err) { setErro((err as Error).message); }
  }

  async function excluir(item: Unidade) {
    if (!window.confirm("Excluir este registro? Ele ficará inativo.")) return;
    try { await excluirUnidade(item.id); setOk("Registro excluído."); carregar(); } catch (err) { setErro((err as Error).message); }
  }

  const set = (k: string, v: unknown) => setForm((f) => ({ ...(f as Form), [k]: v }));

  return (
    <section>
      <div className="cabecalho-secao">
        <h1>Unidades</h1>
        {podeEscrever && !form && <button type="button" onClick={() => { setForm({ ...VAZIO }); setEditando(null); }}>Novo</button>}
      </div>
      <form role="search" className="form-grade" onSubmit={(e) => { e.preventDefault(); setPagina(1); carregar(); }}>
        <div className="largo"><label htmlFor="busca-unidades">Pesquisar</label>
          <input id="busca-unidades" type="search" value={q} onChange={(e) => setQ(e.target.value)} maxLength={200} /></div>
      </form>
      {form && (
        <form onSubmit={salvar} className="form-grade" aria-label="Dados de Unidades">
          <div><label htmlFor="unidades-nome">Nome *</label><input id="unidades-nome" type="text" maxLength={150} value={(form.nome ?? "") as string} onChange={(e) => set("nome", e.target.value)} /></div>
          <div><label htmlFor="unidades-sigla">Sigla *</label><input id="unidades-sigla" type="text" maxLength={20} value={(form.sigla ?? "") as string} onChange={(e) => set("sigla", e.target.value)} /></div>
          <div><label htmlFor="unidades-municipio">Município *</label><input id="unidades-municipio" type="text" maxLength={100} value={(form.municipio ?? "") as string} onChange={(e) => set("municipio", e.target.value)} /></div>
          <div><label htmlFor="unidades-telefone">Telefone</label><input id="unidades-telefone" type="text" maxLength={20} value={(form.telefone ?? "") as string} onChange={(e) => set("telefone", e.target.value)} /></div>
          <div className="largo"><button type="submit">{editando ? "Salvar alterações" : "Cadastrar"}</button>
            {" "}<button type="button" onClick={() => { setForm(null); setEditando(null); }}>Cancelar</button></div>
        </form>
      )}
      <Alerta>{erro}</Alerta>
      <Alerta tipo="sucesso">{ok}</Alerta>
      {res && (<>
        <div className="tabela-rolagem"><table>
          <caption className="sr-only">Unidades</caption>
          <thead><tr><th scope="col">Nome</th><th scope="col">Sigla</th><th scope="col">Município</th><th scope="col">Telefone</th><th scope="col">Ações</th></tr></thead>
          <tbody>{res.itens.map((x) => (
            <tr key={x.id}><td>{String(x.nome ?? "—")}</td><td>{String(x.sigla ?? "—")}</td><td>{String(x.municipio ?? "—")}</td><td>{String(x.telefone ?? "—")}</td><td>{podeEscrever && <button type="button" onClick={() => { const { id, ativo, criado_em, atualizado_em, ...d } = x; void id; void ativo; void criado_em; void atualizado_em; setForm(d as Form); setEditando(x.id); }}>Editar</button>}{" "}{podeExcluir && <button type="button" onClick={() => excluir(x)}>Excluir</button>}</td></tr>
          ))}</tbody>
        </table></div>
        {res.itens.length === 0 && <p className="vazio">Nenhum registro.</p>}
        <Paginacao pagina={res.pagina} total={res.total} porPagina={res.por_pagina} aoMudar={setPagina} />
      </>)}
    </section>
  );
}
