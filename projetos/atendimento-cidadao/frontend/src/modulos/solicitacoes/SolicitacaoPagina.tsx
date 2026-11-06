// MOD-103 — Solicitações: lista, busca, cadastro, edição e exclusão (gerado pela fábrica).
import { useCallback, useEffect, useState } from "react";
import { api, qs, type Pagina } from "../../api/client";
import { useAuth } from "../../auth";
import { Alerta } from "../../components/Alerta";
import { Paginacao } from "../../components/Paginacao";
import { alterarSolicitacao, criarSolicitacao, excluirSolicitacao, listarSolicitacao, type Solicitacao, type SolicitacaoDados } from "./api";

const ESCREVER = ["ADMIN", "GESTOR", "OPERADOR"];
const EXCLUIR = ["ADMIN", "GESTOR"];
type Form = Record<keyof SolicitacaoDados, unknown>;
const VAZIO: Form = { protocolo: "", cidadao_id: null, unidade_id: null, canal: "PRESENCIAL", assunto: "", descricao: "", situacao: "ABERTA", prazo: "", prioritaria: false };

export function validarSolicitacao(d: Form): string | null {
  if (d.protocolo === "" || d.protocolo === null || d.protocolo === undefined) return "Protocolo é obrigatório";
  if (typeof d.protocolo === "string" && d.protocolo.length > 30) return "Protocolo: máximo de 30 caracteres";
  if (d.cidadao_id === "" || d.cidadao_id === null || d.cidadao_id === undefined) return "Cidadão é obrigatório";
  if (d.unidade_id === "" || d.unidade_id === null || d.unidade_id === undefined) return "Unidade é obrigatório";
  if (d.canal === "" || d.canal === null || d.canal === undefined) return "Canal é obrigatório";
  if (d.assunto === "" || d.assunto === null || d.assunto === undefined) return "Assunto é obrigatório";
  if (typeof d.assunto === "string" && d.assunto.length > 200) return "Assunto: máximo de 200 caracteres";
  if (typeof d.descricao === "string" && d.descricao.length > 5000) return "Descrição: máximo de 5000 caracteres";
  if (d.situacao === "" || d.situacao === null || d.situacao === undefined) return "Situação é obrigatório";
  return null;
}

function paraEnvio(d: Form): SolicitacaoDados {
  const saida: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(d)) saida[k] = v === "" ? null : v;
  return saida as unknown as SolicitacaoDados;
}

export function SolicitacaoPagina() {
  const { usuario } = useAuth();
  const podeEscrever = !!usuario && ESCREVER.includes(usuario.perfil);
  const podeExcluir = !!usuario && EXCLUIR.includes(usuario.perfil);
  const [res, setRes] = useState<Pagina<Solicitacao> | null>(null);
  const [q, setQ] = useState("");
  const [pagina, setPagina] = useState(1);
  const [form, setForm] = useState<Form | null>(null);
  const [editando, setEditando] = useState<number | null>(null);
  const [erro, setErro] = useState("");
  const [ok, setOk] = useState("");
  const [op_cidadao_id, setOp_cidadao_id] = useState<{ id: number; rotulo: string }[]>([]);
  const [op_unidade_id, setOp_unidade_id] = useState<{ id: number; rotulo: string }[]>([]);

  const carregar = useCallback(() => { listarSolicitacao(q, pagina).then(setRes).catch((e) => setErro(e.message)); }, [q, pagina]);
  useEffect(carregar, [carregar]);
  useEffect(() => { api<Pagina<Record<string, unknown>>>(`/api/cidadaos${qs({ por_pagina: 100 })}`).then((p) => setOp_cidadao_id(p.itens.map((x) => ({ id: Number(x.id), rotulo: String(x.nome) })))).catch(() => {}); }, []);
  useEffect(() => { api<Pagina<Record<string, unknown>>>(`/api/unidades${qs({ por_pagina: 100 })}`).then((p) => setOp_unidade_id(p.itens.map((x) => ({ id: Number(x.id), rotulo: String(x.nome) })))).catch(() => {}); }, []);

  async function salvar(e: React.FormEvent) {
    e.preventDefault(); setErro(""); setOk("");
    if (!form) return;
    const problema = validarSolicitacao(form);
    if (problema) { setErro(problema); return; }
    try {
      if (editando) await alterarSolicitacao(editando, paraEnvio(form)); else await criarSolicitacao(paraEnvio(form));
      setOk("Salvo com sucesso."); setForm(null); setEditando(null); carregar();
    } catch (err) { setErro((err as Error).message); }
  }

  async function excluir(item: Solicitacao) {
    if (!window.confirm("Excluir este registro? Ele ficará inativo.")) return;
    try { await excluirSolicitacao(item.id); setOk("Registro excluído."); carregar(); } catch (err) { setErro((err as Error).message); }
  }

  const set = (k: string, v: unknown) => setForm((f) => ({ ...(f as Form), [k]: v }));

  return (
    <section>
      <div className="cabecalho-secao">
        <h1>Solicitações</h1>
        {podeEscrever && !form && <button type="button" onClick={() => { setForm({ ...VAZIO }); setEditando(null); }}>Novo</button>}
      </div>
      <form role="search" className="form-grade" onSubmit={(e) => { e.preventDefault(); setPagina(1); carregar(); }}>
        <div className="largo"><label htmlFor="busca-solicitacoes">Pesquisar</label>
          <input id="busca-solicitacoes" type="search" value={q} onChange={(e) => setQ(e.target.value)} maxLength={200} /></div>
      </form>
      {form && (
        <form onSubmit={salvar} className="form-grade" aria-label="Dados de Solicitações">
          <div><label htmlFor="solicitacoes-protocolo">Protocolo *</label><input id="solicitacoes-protocolo" type="text" maxLength={30} value={(form.protocolo ?? "") as string} onChange={(e) => set("protocolo", e.target.value)} /></div>
          <div><label htmlFor="solicitacoes-cidadao_id">Cidadão *</label><select id="solicitacoes-cidadao_id" value={String(form.cidadao_id ?? "")} onChange={(e) => set("cidadao_id", e.target.value ? Number(e.target.value) : null)}><option value="">Selecione…</option>{op_cidadao_id.map((o) => <option key={o.id} value={o.id}>{o.rotulo}</option>)}</select></div>
          <div><label htmlFor="solicitacoes-unidade_id">Unidade *</label><select id="solicitacoes-unidade_id" value={String(form.unidade_id ?? "")} onChange={(e) => set("unidade_id", e.target.value ? Number(e.target.value) : null)}><option value="">Selecione…</option>{op_unidade_id.map((o) => <option key={o.id} value={o.id}>{o.rotulo}</option>)}</select></div>
          <div><label htmlFor="solicitacoes-canal">Canal *</label><select id="solicitacoes-canal" value={(form.canal ?? "") as string} onChange={(e) => set("canal", e.target.value)}><option value="PRESENCIAL">PRESENCIAL</option><option value="PORTAL">PORTAL</option><option value="TELEFONE">TELEFONE</option><option value="WHATSAPP">WHATSAPP</option></select></div>
          <div><label htmlFor="solicitacoes-assunto">Assunto *</label><input id="solicitacoes-assunto" type="text" maxLength={200} value={(form.assunto ?? "") as string} onChange={(e) => set("assunto", e.target.value)} /></div>
          <div className="largo"><label htmlFor="solicitacoes-descricao">Descrição</label><textarea id="solicitacoes-descricao" rows={3} value={(form.descricao ?? "") as string} onChange={(e) => set("descricao", e.target.value)} /></div>
          <div><label htmlFor="solicitacoes-situacao">Situação *</label><select id="solicitacoes-situacao" value={(form.situacao ?? "") as string} onChange={(e) => set("situacao", e.target.value)}><option value="ABERTA">ABERTA</option><option value="EM_ATENDIMENTO">EM_ATENDIMENTO</option><option value="CONCLUIDA">CONCLUIDA</option><option value="CANCELADA">CANCELADA</option></select></div>
          <div><label htmlFor="solicitacoes-prazo">Prazo</label><input id="solicitacoes-prazo" type="date" value={(form.prazo ?? "") as string} onChange={(e) => set("prazo", e.target.value)} /></div>
          <div><label htmlFor="solicitacoes-prioritaria">Prioritária</label><input id="solicitacoes-prioritaria" type="checkbox" checked={!!form.prioritaria} onChange={(e) => set("prioritaria", e.target.checked)} /></div>
          <div className="largo"><button type="submit">{editando ? "Salvar alterações" : "Cadastrar"}</button>
            {" "}<button type="button" onClick={() => { setForm(null); setEditando(null); }}>Cancelar</button></div>
        </form>
      )}
      <Alerta>{erro}</Alerta>
      <Alerta tipo="sucesso">{ok}</Alerta>
      {res && (<>
        <div className="tabela-rolagem"><table>
          <caption className="sr-only">Solicitações</caption>
          <thead><tr><th scope="col">Protocolo</th><th scope="col">Cidadão</th><th scope="col">Unidade</th><th scope="col">Canal</th><th scope="col">Assunto</th><th scope="col">Situação</th><th scope="col">Ações</th></tr></thead>
          <tbody>{res.itens.map((x) => (
            <tr key={x.id}><td>{String(x.protocolo ?? "—")}</td><td>{op_cidadao_id.find((o) => o.id === x.cidadao_id)?.rotulo ?? String(x.cidadao_id ?? "—")}</td><td>{op_unidade_id.find((o) => o.id === x.unidade_id)?.rotulo ?? String(x.unidade_id ?? "—")}</td><td>{String(x.canal ?? "—")}</td><td>{String(x.assunto ?? "—")}</td><td>{String(x.situacao ?? "—")}</td><td>{podeEscrever && <button type="button" onClick={() => { const { id, ativo, criado_em, atualizado_em, ...d } = x; void id; void ativo; void criado_em; void atualizado_em; setForm(d as Form); setEditando(x.id); }}>Editar</button>}{" "}{podeExcluir && <button type="button" onClick={() => excluir(x)}>Excluir</button>}</td></tr>
          ))}</tbody>
        </table></div>
        {res.itens.length === 0 && <p className="vazio">Nenhum registro.</p>}
        <Paginacao pagina={res.pagina} total={res.total} porPagina={res.por_pagina} aoMudar={setPagina} />
      </>)}
    </section>
  );
}
