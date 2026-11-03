// MOD-006 — Consulta à trilha de auditoria.
import { useCallback, useEffect, useState } from "react";
import { api, dataBR, qs, type Pagina, type RegistroAuditoria } from "../api/client";
import { Alerta } from "../components/Alerta";
import { Paginacao } from "../components/Paginacao";

export function Auditoria() {
  const [acoes, setAcoes] = useState<string[]>([]);
  const [f, setF] = useState({ acao: "", de: "", ate: "" });
  const [pagina, setPagina] = useState(1);
  const [res, setRes] = useState<Pagina<RegistroAuditoria> | null>(null);
  const [erro, setErro] = useState("");
  useEffect(() => { api<string[]>("/api/auditoria/acoes").then(setAcoes).catch(() => {}); }, []);
  const carregar = useCallback(() => {
    api<Pagina<RegistroAuditoria>>(`/api/auditoria${qs({ ...f, pagina, por_pagina: 50 })}`).then(setRes).catch((e) => setErro(e.message));
  }, [f, pagina]);
  useEffect(carregar, [carregar]);
  return (
    <section>
      <h1>Auditoria</h1>
      <p className="meta">Registros somente leitura. Nenhuma ação desta tela altera a trilha.</p>
      <div className="form-grade">
        <div><label htmlFor="aacao">Ação</label><select id="aacao" value={f.acao} onChange={(e) => { setF({ ...f, acao: e.target.value }); setPagina(1); }}>
          <option value="">Todas</option>{acoes.map((a) => <option key={a}>{a}</option>)}</select></div>
        <div><label htmlFor="ade">De</label><input id="ade" type="date" value={f.de} onChange={(e) => { setF({ ...f, de: e.target.value }); setPagina(1); }} /></div>
        <div><label htmlFor="aate">Até</label><input id="aate" type="date" value={f.ate} onChange={(e) => { setF({ ...f, ate: e.target.value }); setPagina(1); }} /></div>
      </div>
      <Alerta>{erro}</Alerta>
      {res && (<>
        <div className="tabela-rolagem"><table>
          <thead><tr><th scope="col">Momento</th><th scope="col">Usuário</th><th scope="col">Ação</th><th scope="col">Recurso</th><th scope="col">IP</th><th scope="col">Detalhes</th></tr></thead>
          <tbody>{res.itens.map((a) => (
            <tr key={a.id}><td>{dataBR(a.momento)}</td><td>{a.usuario_id ?? "—"}</td><td>{a.acao}</td><td>{a.recurso} {a.recurso_id}</td><td>{a.ip}</td><td><code>{a.detalhes}</code></td></tr>))}
          </tbody></table></div>
        <Paginacao pagina={pagina} total={res.total} porPagina={res.por_pagina} aoMudar={setPagina} />
      </>)}
    </section>
  );
}
