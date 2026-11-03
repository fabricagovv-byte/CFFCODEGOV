// MOD-102 — Protocolos: lista, busca, cadastro, edição e exclusão (gerado pela fábrica).
import { useCallback, useEffect, useState } from "react";
import { api, qs, type Pagina } from "../../api/client";
import { useAuth } from "../../auth";
import { Alerta } from "../../components/Alerta";
import { Paginacao } from "../../components/Paginacao";
import { alterarProtocolo, criarProtocolo, excluirProtocolo, listarProtocolo, type Protocolo, type ProtocoloDados } from "./api";

const ESCREVER = ["ADMIN", "GESTOR", "OPERADOR"];
const EXCLUIR = ["ADMIN", "GESTOR"];
type Form = Record<keyof ProtocoloDados, unknown>;
const VAZIO: Form = { numero: "", assunto: "", interessado_id: null, canal: "PRESENCIAL", prioridade: "NORMAL", prazo: "", valor_taxa: "", quantidade_folhas: null, sigiloso: false };

export function validarProtocolo(d: Form): string | null {
  if (d.numero === "" || d.numero === null || d.numero === undefined) return "Número é obrigatório";
  if (typeof d.numero === "string" && d.numero.length > 30) return "Número: máximo de 30 caracteres";
  if (d.assunto === "" || d.assunto === null || d.assunto === undefined) return "Assunto é obrigatório";
  if (typeof d.assunto === "string" && d.assunto.length > 200) return "Assunto: máximo de 200 caracteres";
  if (d.interessado_id === "" || d.interessado_id === null || d.interessado_id === undefined) return "Interessado é obrigatório";
  if (d.canal === "" || d.canal === null || d.canal === undefined) return "Canal é obrigatório";
  if (d.prioridade === "" || d.prioridade === null || d.prioridade === undefined) return "Prioridade é obrigatório";
  return null;
}

function paraEnvio(d: Form): ProtocoloDados {
  const saida: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(d)) saida[k] = v === "" ? null : v;
  return saida as unknown as ProtocoloDados;
}

export function ProtocoloPagina() {
  const { usuario } = useAuth();
  const podeEscrever = !!usuario && ESCREVER.includes(usuario.perfil);
  const podeExcluir = !!usuario && EXCLUIR.includes(usuario.perfil);
  const [res, setRes] = useState<Pagina<Protocolo> | null>(null);
  const [q, setQ] = useState("");
  const [pagina, setPagina] = useState(1);
  const [form, setForm] = useState<Form | null>(null);
  const [editando, setEditando] = useState<number | null>(null);
  const [erro, setErro] = useState("");
  const [ok, setOk] = useState("");
  const [op_interessado_id, setOp_interessado_id] = useState<{ id: number; rotulo: string }[]>([]);

  const carregar = useCallback(() => { listarProtocolo(q, pagina).then(setRes).catch((e) => setErro(e.message)); }, [q, pagina]);
  useEffect(carregar, [carregar]);
  useEffect(() => { api<Pagina<Record<string, unknown>>>(`/api/interessados${qs({ por_pagina: 100 })}`).then((p) => setOp_interessado_id(p.itens.map((x) => ({ id: Number(x.id), rotulo: String(x.nome) })))).catch(() => {}); }, []);

  async function salvar(e: React.FormEvent) {
    e.preventDefault(); setErro(""); setOk("");
    if (!form) return;
    const problema = validarProtocolo(form);
    if (problema) { setErro(problema); return; }
    try {
      if (editando) await alterarProtocolo(editando, paraEnvio(form)); else await criarProtocolo(paraEnvio(form));
      setOk("Salvo com sucesso."); setForm(null); setEditando(null); carregar();
    } catch (err) { setErro((err as Error).message); }
  }

  async function excluir(item: Protocolo) {
    if (!window.confirm("Excluir este registro? Ele ficará inativo.")) return;
    try { await excluirProtocolo(item.id); setOk("Registro excluído."); carregar(); } catch (err) { setErro((err as Error).message); }
  }

  const set = (k: string, v: unknown) => setForm((f) => ({ ...(f as Form), [k]: v }));

  return (
    <section>
      <div className="cabecalho-secao">
        <h1>Protocolos</h1>
        {podeEscrever && !form && <button type="button" onClick={() => { setForm({ ...VAZIO }); setEditando(null); }}>Novo</button>}
      </div>
      <form role="search" className="form-grade" onSubmit={(e) => { e.preventDefault(); setPagina(1); carregar(); }}>
        <div className="largo"><label htmlFor="busca-protocolos">Pesquisar</label>
          <input id="busca-protocolos" type="search" value={q} onChange={(e) => setQ(e.target.value)} maxLength={200} /></div>
      </form>
      {form && (
        <form onSubmit={salvar} className="form-grade" aria-label="Dados de Protocolos">
          <div><label htmlFor="protocolos-numero">Número *</label><input id="protocolos-numero" type="text" maxLength={30} value={(form.numero ?? "") as string} onChange={(e) => set("numero", e.target.value)} /></div>
          <div><label htmlFor="protocolos-assunto">Assunto *</label><input id="protocolos-assunto" type="text" maxLength={200} value={(form.assunto ?? "") as string} onChange={(e) => set("assunto", e.target.value)} /></div>
          <div><label htmlFor="protocolos-interessado_id">Interessado *</label><select id="protocolos-interessado_id" value={String(form.interessado_id ?? "")} onChange={(e) => set("interessado_id", e.target.value ? Number(e.target.value) : null)}><option value="">Selecione…</option>{op_interessado_id.map((o) => <option key={o.id} value={o.id}>{o.rotulo}</option>)}</select></div>
          <div><label htmlFor="protocolos-canal">Canal *</label><select id="protocolos-canal" value={(form.canal ?? "") as string} onChange={(e) => set("canal", e.target.value)}><option value="PRESENCIAL">PRESENCIAL</option><option value="EMAIL">EMAIL</option><option value="PORTAL">PORTAL</option><option value="TELEFONE">TELEFONE</option></select></div>
          <div><label htmlFor="protocolos-prioridade">Prioridade *</label><select id="protocolos-prioridade" value={(form.prioridade ?? "") as string} onChange={(e) => set("prioridade", e.target.value)}><option value="NORMAL">NORMAL</option><option value="URGENTE">URGENTE</option></select></div>
          <div><label htmlFor="protocolos-prazo">Prazo</label><input id="protocolos-prazo" type="date" value={(form.prazo ?? "") as string} onChange={(e) => set("prazo", e.target.value)} /></div>
          <div><label htmlFor="protocolos-valor_taxa">Valor da taxa (R$)</label><input id="protocolos-valor_taxa" type="number" step="0.01" value={(form.valor_taxa ?? "") as string} onChange={(e) => set("valor_taxa", e.target.value)} /></div>
          <div><label htmlFor="protocolos-quantidade_folhas">Quantidade de folhas</label><input id="protocolos-quantidade_folhas" type="number" value={(form.quantidade_folhas ?? "") as string} onChange={(e) => set("quantidade_folhas", e.target.value === "" ? null : Number(e.target.value))} /></div>
          <div><label htmlFor="protocolos-sigiloso">Sigiloso</label><input id="protocolos-sigiloso" type="checkbox" checked={!!form.sigiloso} onChange={(e) => set("sigiloso", e.target.checked)} /></div>
          <div className="largo"><button type="submit">{editando ? "Salvar alterações" : "Cadastrar"}</button>
            {" "}<button type="button" onClick={() => { setForm(null); setEditando(null); }}>Cancelar</button></div>
        </form>
      )}
      <Alerta>{erro}</Alerta>
      <Alerta tipo="sucesso">{ok}</Alerta>
      {res && (<>
        <div className="tabela-rolagem"><table>
          <caption className="sr-only">Protocolos</caption>
          <thead><tr><th scope="col">Número</th><th scope="col">Assunto</th><th scope="col">Interessado</th><th scope="col">Canal</th><th scope="col">Prioridade</th><th scope="col">Prazo</th><th scope="col">Ações</th></tr></thead>
          <tbody>{res.itens.map((x) => (
            <tr key={x.id}><td>{String(x.numero ?? "—")}</td><td>{String(x.assunto ?? "—")}</td><td>{op_interessado_id.find((o) => o.id === x.interessado_id)?.rotulo ?? String(x.interessado_id ?? "—")}</td><td>{String(x.canal ?? "—")}</td><td>{String(x.prioridade ?? "—")}</td><td>{String(x.prazo ?? "—")}</td><td>{podeEscrever && <button type="button" onClick={() => { const { id, ativo, criado_em, atualizado_em, ...d } = x; void id; void ativo; void criado_em; void atualizado_em; setForm(d as Form); setEditando(x.id); }}>Editar</button>}{" "}{podeExcluir && <button type="button" onClick={() => excluir(x)}>Excluir</button>}</td></tr>
          ))}</tbody>
        </table></div>
        {res.itens.length === 0 && <p className="vazio">Nenhum registro.</p>}
        <Paginacao pagina={res.pagina} total={res.total} porPagina={res.por_pagina} aoMudar={setPagina} />
      </>)}
    </section>
  );
}
