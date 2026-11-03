// MOD-002/MOD-003 — Detalhe, edição e anexos do documento.
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, baixarArquivo, dataBR, formatarBytes, json, type Documento } from "../api/client";
import { useAuth } from "../auth";
import { Alerta } from "../components/Alerta";
import { UploadPdf } from "../components/UploadPdf";
import { FormDocumento, type DadosDocumento } from "./FormDocumento";

export function DocumentoDetalhe() {
  const { id } = useParams();
  const { pode } = useAuth();
  const [doc, setDoc] = useState<Documento | null>(null);
  const [erro, setErro] = useState("");
  const [erroDownload, setErroDownload] = useState("");
  const carregar = useCallback(() => { api<Documento>(`/api/documentos/${id}`).then(setDoc).catch((e) => setErro(e.message)); }, [id]);
  useEffect(carregar, [carregar]);

  async function salvar(d: DadosDocumento) {
    setDoc(await api<Documento>(`/api/documentos/${id}`, { method: "PATCH", body: json(d) }));
  }

  if (erro) return <Alerta>{erro}</Alerta>;
  if (!doc) return <p aria-busy="true">Carregando…</p>;
  return (
    <section>
      <p><Link to="/documentos">← Documentos</Link></p>
      <h1>{doc.numero} — {doc.titulo}</h1>
      <p className="meta">Criado em {dataBR(doc.criado_em)} · Atualizado em {dataBR(doc.atualizado_em)}</p>
      {pode("doc:editar") && (doc.status !== "ARQUIVADO" || pode("doc:arquivar")) ? <FormDocumento key={doc.id} inicial={doc} aoSalvar={salvar} rotulo="Salvar alterações" /> : (
        <dl className="detalhes">
          <dt>Tipo</dt><dd>{doc.tipo}</dd><dt>Interessado</dt><dd>{doc.interessado || "—"}</dd>
          <dt>Classificação</dt><dd>{doc.classificacao}</dd><dt>Status</dt><dd>{doc.status}</dd><dt>Assunto</dt><dd>{doc.assunto || "—"}</dd>
        </dl>
      )}
      <h2>Anexos ({doc.arquivos.length})</h2>
      {doc.arquivos.length ? (
        <ul className="anexos">
          {doc.arquivos.map((a) => (
            <li key={a.id}>
              <button type="button" className="link" onClick={() => { setErroDownload(""); baixarArquivo(a).catch((e) => setErroDownload(e.message)); }}>{a.nome_original}</button>
              {" "}<span className="meta">{formatarBytes(a.tamanho)} · SHA-256 {a.sha256.slice(0, 12)}… · {dataBR(a.enviado_em)}</span>
            </li>
          ))}
        </ul>
      ) : <p className="vazio">Nenhum anexo.</p>}
      <Alerta>{erroDownload}</Alerta>
      {pode("arquivo:enviar") && doc.status !== "ARQUIVADO" && <UploadPdf documentoId={doc.id} aoEnviar={carregar} />}
    </section>
  );
}
