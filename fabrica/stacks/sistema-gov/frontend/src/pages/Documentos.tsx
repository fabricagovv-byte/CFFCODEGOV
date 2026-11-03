// MOD-002 — Lista e cadastro de documentos.
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, json, qs, type Documento, type Pagina } from "../api/client";
import { useAuth } from "../auth";
import { Alerta } from "../components/Alerta";
import { Paginacao } from "../components/Paginacao";
import { TabelaDocumentos } from "../components/TabelaDocumentos";
import { FormDocumento, type DadosDocumento } from "./FormDocumento";

export function Documentos() {
  const { pode } = useAuth();
  const nav = useNavigate();
  const [pag, setPag] = useState<Pagina<Documento> | null>(null);
  const [pagina, setPagina] = useState(1);
  const [status, setStatus] = useState("");
  const [erro, setErro] = useState("");
  const [novo, setNovo] = useState(false);

  const carregar = useCallback(() => {
    api<Pagina<Documento>>(`/api/documentos${qs({ pagina, por_pagina: 20, status })}`).then(setPag).catch((e) => setErro(e.message));
  }, [pagina, status]);
  useEffect(carregar, [carregar]);

  async function criar(d: DadosDocumento) {
    const doc = await api<Documento>("/api/documentos", { method: "POST", body: json(d) });
    nav(`/documentos/${doc.id}`);
  }

  return (
    <section>
      <div className="cabecalho-secao">
        <h1>Documentos</h1>
        {pode("doc:criar") && <button type="button" onClick={() => setNovo(!novo)}>{novo ? "Cancelar" : "Novo documento"}</button>}
      </div>
      {novo && <FormDocumento aoSalvar={criar} rotulo="Cadastrar" />}
      <label htmlFor="filtro-status">Status</label>
      <select id="filtro-status" value={status} onChange={(e) => { setStatus(e.target.value); setPagina(1); }}>
        <option value="">Todos</option><option>ATIVO</option><option>RASCUNHO</option><option>ARQUIVADO</option>
      </select>
      <Alerta>{erro}</Alerta>
      {pag && <><TabelaDocumentos itens={pag.itens} /><Paginacao pagina={pag.pagina} total={pag.total} porPagina={pag.por_pagina} aoMudar={setPagina} /></>}
    </section>
  );
}
