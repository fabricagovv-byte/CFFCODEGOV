// MOD-101 — Interessados: lista, busca, cadastro, edição e exclusão (gerado pela fábrica).
import { useCallback, useEffect, useState } from "react";
import type { Pagina } from "../../api/client";
import { useAuth } from "../../auth";
import { Alerta } from "../../components/Alerta";
import { Paginacao } from "../../components/Paginacao";
import { alterarInteressado, criarInteressado, excluirInteressado, listarInteressado, type Interessado, type InteressadoDados } from "./api";

const ESCREVER = ["ADMIN", "GESTOR", "OPERADOR"];
const EXCLUIR = ["ADMIN", "GESTOR"];
type Form = Record<keyof InteressadoDados, unknown>;
const VAZIO: Form = { nome: "", documento: "", tipo_pessoa: "FISICA", email: "", telefone: "", observacoes: "" };

export function validarInteressado(d: Form): string | null {
  if (d.nome === "" || d.nome === null || d.nome === undefined) return "Nome é obrigatório";
  if (typeof d.nome === "string" && d.nome.length > 150) return "Nome: máximo de 150 caracteres";
  if (d.documento === "" || d.documento === null || d.documento === undefined) return "CPF/CNPJ é obrigatório";
  if (d.tipo_pessoa === "" || d.tipo_pessoa === null || d.tipo_pessoa === undefined) return "Tipo de pessoa é obrigatório";
  if (typeof d.email === "string" && d.email.length > 254) return "E-mail: máximo de 254 caracteres";
  if (d.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(String(d.email))) return "E-mail: e-mail inválido";
  if (typeof d.telefone === "string" && d.telefone.length > 20) return "Telefone: máximo de 20 caracteres";
  if (typeof d.observacoes === "string" && d.observacoes.length > 5000) return "Observações: máximo de 5000 caracteres";
  return null;
}

function paraEnvio(d: Form): InteressadoDados {
  const saida: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(d)) saida[k] = v === "" ? null : v;
  return saida as unknown as InteressadoDados;
}

export function InteressadoPagina() {
  const { usuario } = useAuth();
  const podeEscrever = !!usuario && ESCREVER.includes(usuario.perfil);
  const podeExcluir = !!usuario && EXCLUIR.includes(usuario.perfil);
  const [res, setRes] = useState<Pagina<Interessado> | null>(null);
  const [q, setQ] = useState("");
  const [pagina, setPagina] = useState(1);
  const [form, setForm] = useState<Form | null>(null);
  const [editando, setEditando] = useState<number | null>(null);
  const [erro, setErro] = useState("");
  const [ok, setOk] = useState("");

  const carregar = useCallback(() => { listarInteressado(q, pagina).then(setRes).catch((e) => setErro(e.message)); }, [q, pagina]);
  useEffect(carregar, [carregar]);

  async function salvar(e: React.FormEvent) {
    e.preventDefault(); setErro(""); setOk("");
    if (!form) return;
    const problema = validarInteressado(form);
    if (problema) { setErro(problema); return; }
    try {
      if (editando) await alterarInteressado(editando, paraEnvio(form)); else await criarInteressado(paraEnvio(form));
      setOk("Salvo com sucesso."); setForm(null); setEditando(null); carregar();
    } catch (err) { setErro((err as Error).message); }
  }

  async function excluir(item: Interessado) {
    if (!window.confirm("Excluir este registro? Ele ficará inativo.")) return;
    try { await excluirInteressado(item.id); setOk("Registro excluído."); carregar(); } catch (err) { setErro((err as Error).message); }
  }

  const set = (k: string, v: unknown) => setForm((f) => ({ ...(f as Form), [k]: v }));

  return (
    <section>
      <div className="cabecalho-secao">
        <h1>Interessados</h1>
        {podeEscrever && !form && <button type="button" onClick={() => { setForm({ ...VAZIO }); setEditando(null); }}>Novo</button>}
      </div>
      <form role="search" className="form-grade" onSubmit={(e) => { e.preventDefault(); setPagina(1); carregar(); }}>
        <div className="largo"><label htmlFor="busca-interessados">Pesquisar</label>
          <input id="busca-interessados" type="search" value={q} onChange={(e) => setQ(e.target.value)} maxLength={200} /></div>
      </form>
      {form && (
        <form onSubmit={salvar} className="form-grade" aria-label="Dados de Interessados">
          <div><label htmlFor="interessados-nome">Nome *</label><input id="interessados-nome" type="text" maxLength={150} value={(form.nome ?? "") as string} onChange={(e) => set("nome", e.target.value)} /></div>
          <div><label htmlFor="interessados-documento">CPF/CNPJ *</label><input id="interessados-documento" type="text" value={(form.documento ?? "") as string} onChange={(e) => set("documento", e.target.value)} /></div>
          <div><label htmlFor="interessados-tipo_pessoa">Tipo de pessoa *</label><select id="interessados-tipo_pessoa" value={(form.tipo_pessoa ?? "") as string} onChange={(e) => set("tipo_pessoa", e.target.value)}><option value="FISICA">FISICA</option><option value="JURIDICA">JURIDICA</option></select></div>
          <div><label htmlFor="interessados-email">E-mail</label><input id="interessados-email" type="email" maxLength={254} value={(form.email ?? "") as string} onChange={(e) => set("email", e.target.value)} /></div>
          <div><label htmlFor="interessados-telefone">Telefone</label><input id="interessados-telefone" type="text" maxLength={20} value={(form.telefone ?? "") as string} onChange={(e) => set("telefone", e.target.value)} /></div>
          <div className="largo"><label htmlFor="interessados-observacoes">Observações</label><textarea id="interessados-observacoes" rows={3} value={(form.observacoes ?? "") as string} onChange={(e) => set("observacoes", e.target.value)} /></div>
          <div className="largo"><button type="submit">{editando ? "Salvar alterações" : "Cadastrar"}</button>
            {" "}<button type="button" onClick={() => { setForm(null); setEditando(null); }}>Cancelar</button></div>
        </form>
      )}
      <Alerta>{erro}</Alerta>
      <Alerta tipo="sucesso">{ok}</Alerta>
      {res && (<>
        <div className="tabela-rolagem"><table>
          <caption className="sr-only">Interessados</caption>
          <thead><tr><th scope="col">Nome</th><th scope="col">CPF/CNPJ</th><th scope="col">Tipo de pessoa</th><th scope="col">E-mail</th><th scope="col">Telefone</th><th scope="col">Ações</th></tr></thead>
          <tbody>{res.itens.map((x) => (
            <tr key={x.id}><td>{String(x.nome ?? "—")}</td><td>{String(x.documento ?? "—")}</td><td>{String(x.tipo_pessoa ?? "—")}</td><td>{String(x.email ?? "—")}</td><td>{String(x.telefone ?? "—")}</td><td>{podeEscrever && <button type="button" onClick={() => { const { id, ativo, criado_em, atualizado_em, ...d } = x; void id; void ativo; void criado_em; void atualizado_em; setForm(d as Form); setEditando(x.id); }}>Editar</button>}{" "}{podeExcluir && <button type="button" onClick={() => excluir(x)}>Excluir</button>}</td></tr>
          ))}</tbody>
        </table></div>
        {res.itens.length === 0 && <p className="vazio">Nenhum registro.</p>}
        <Paginacao pagina={res.pagina} total={res.total} porPagina={res.por_pagina} aoMudar={setPagina} />
      </>)}
    </section>
  );
}
