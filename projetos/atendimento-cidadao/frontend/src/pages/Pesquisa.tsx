// MOD-004 — Pesquisa documental.
import { useEffect, useState } from "react";
import { api, qs, type Documento, type Pagina } from "../api/client";
import { Alerta } from "../components/Alerta";
import { Paginacao } from "../components/Paginacao";
import { TabelaDocumentos } from "../components/TabelaDocumentos";

export function Pesquisa() {
  const [f, setF] = useState({ q: "", tipo: "", status: "", de: "", ate: "" });
  const [pagina, setPagina] = useState(1);
  const [res, setRes] = useState<Pagina<Documento> | null>(null);
  const [tipos, setTipos] = useState<string[]>([]);
  const [erro, setErro] = useState("");

  useEffect(() => { api<string[]>("/api/pesquisa/tipos").then(setTipos).catch(() => {}); }, []);

  async function buscar(p = 1) {
    setErro(""); setPagina(p);
    try { setRes(await api<Pagina<Documento>>(`/api/pesquisa${qs({ ...f, pagina: p, por_pagina: 20 })}`)); }
    catch (e) { setErro((e as Error).message); }
  }
  const set = (k: keyof typeof f) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setF({ ...f, [k]: e.target.value });

  return (
    <section>
      <h1>Pesquisa</h1>
      <form role="search" className="form-grade" onSubmit={(e) => { e.preventDefault(); buscar(1); }}>
        <div className="largo"><label htmlFor="q">Termos (número, título, assunto, interessado ou nome do arquivo)</label>
          <input id="q" type="search" value={f.q} onChange={set("q")} maxLength={200} /></div>
        <div><label htmlFor="ptipo">Tipo</label><select id="ptipo" value={f.tipo} onChange={set("tipo")}><option value="">Todos</option>{tipos.map((t) => <option key={t}>{t}</option>)}</select></div>
        <div><label htmlFor="pstatus">Status</label><select id="pstatus" value={f.status} onChange={set("status")}><option value="">Todos</option><option>ATIVO</option><option>RASCUNHO</option><option>ARQUIVADO</option></select></div>
        <div><label htmlFor="de">De</label><input id="de" type="date" value={f.de} onChange={set("de")} /></div>
        <div><label htmlFor="ate">Até</label><input id="ate" type="date" value={f.ate} onChange={set("ate")} /></div>
        <div className="largo"><button type="submit">Pesquisar</button></div>
      </form>
      <Alerta>{erro}</Alerta>
      {res && <><p role="status">{res.total} resultado(s)</p><TabelaDocumentos itens={res.itens} />
        <Paginacao pagina={pagina} total={res.total} porPagina={res.por_pagina} aoMudar={buscar} /></>}
    </section>
  );
}
