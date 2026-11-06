import { Link } from "react-router-dom";
import { dataBR, type Documento } from "../api/client";

export function TabelaDocumentos({ itens }: { itens: Documento[] }) {
  if (!itens.length) return <p className="vazio">Nenhum documento encontrado.</p>;
  return (
    <div className="tabela-rolagem">
      <table>
        <caption className="sr-only">Documentos</caption>
        <thead>
          <tr><th scope="col">Número</th><th scope="col">Título</th><th scope="col">Tipo</th><th scope="col">Classificação</th><th scope="col">Status</th><th scope="col">Anexos</th><th scope="col">Criado em</th></tr>
        </thead>
        <tbody>
          {itens.map((d) => (
            <tr key={d.id}>
              <td><Link to={`/documentos/${d.id}`}>{d.numero}</Link></td>
              <td>{d.titulo}</td><td>{d.tipo}</td>
              <td><span className={`etiqueta cls-${d.classificacao.toLowerCase()}`}>{d.classificacao}</span></td>
              <td>{d.status}</td><td>{d.arquivos.length}</td><td>{dataBR(d.criado_em)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
