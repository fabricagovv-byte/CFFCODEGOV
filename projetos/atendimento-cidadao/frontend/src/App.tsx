import { Navigate, NavLink, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import { Auditoria } from "./pages/Auditoria";
import { DocumentoDetalhe } from "./pages/DocumentoDetalhe";
import { Documentos } from "./pages/Documentos";
import { EsqueciSenha } from "./pages/EsqueciSenha";
import { Login } from "./pages/Login";
import { Painel } from "./pages/Painel";
import { Pesquisa } from "./pages/Pesquisa";
import { RedefinirSenha } from "./pages/RedefinirSenha";
import { UnidadePagina } from "./modulos/unidades/UnidadePagina";
import { CidadaoPagina } from "./modulos/cidadaos/CidadaoPagina";
import { SolicitacaoPagina } from "./modulos/solicitacoes/SolicitacaoPagina";
// fabrica:imports

function Protegido({ permissao }: { permissao?: string }) {
  const { usuario, carregando, pode, sair } = useAuth();
  if (carregando) return <p aria-busy="true">Carregando…</p>;
  if (!usuario) return <Navigate to="/login" replace />;
  if (permissao && !pode(permissao)) return <Navigate to="/documentos" replace />;
  return (
    <>
      <a className="pular" href="#conteudo">Pular para o conteúdo</a>
      <header className="topo">
        <span className="marca">Atendimento ao Cidadão</span>
        <nav aria-label="Principal">
          <NavLink to="/documentos">Documentos</NavLink>
          <NavLink to="/pesquisa">Pesquisa</NavLink>
          {pode("painel:ler") && <NavLink to="/painel">Painel</NavLink>}
          {pode("auditoria:ler") && <NavLink to="/auditoria">Auditoria</NavLink>}
          <NavLink to="/unidades">Unidades</NavLink>
          <NavLink to="/cidadaos">Cidadãos</NavLink>
          <NavLink to="/solicitacoes">Solicitações</NavLink>
          {/* fabrica:menu */}
        </nav>
        <span className="usuario">{usuario.nome} ({usuario.perfil})</span>
        <button type="button" onClick={sair}>Sair</button>
      </header>
      <main id="conteudo" className="conteudo"><Outlet /></main>
      <footer className="rodape">Atendimento ao Cidadão · ambiente de demonstração · dados fictícios</footer>
    </>
  );
}

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/esqueci-senha" element={<EsqueciSenha />} />
      <Route path="/redefinir-senha" element={<RedefinirSenha />} />
      <Route element={<Protegido />}>
        <Route path="/documentos" element={<Documentos />} />
        <Route path="/documentos/:id" element={<DocumentoDetalhe />} />
        <Route path="/pesquisa" element={<Pesquisa />} />
        <Route path="/unidades" element={<UnidadePagina />} />
        <Route path="/cidadaos" element={<CidadaoPagina />} />
        <Route path="/solicitacoes" element={<SolicitacaoPagina />} />
        {/* fabrica:rotas */}
      </Route>
      <Route element={<Protegido permissao="painel:ler" />}><Route path="/painel" element={<Painel />} /></Route>
      <Route element={<Protegido permissao="auditoria:ler" />}><Route path="/auditoria" element={<Auditoria />} /></Route>
      <Route path="*" element={<Navigate to="/documentos" replace />} />
    </Routes>
  );
}
