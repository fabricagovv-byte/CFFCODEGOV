// MOD-005 — Painel administrativo (indicadores e usuários).
import { useCallback, useEffect, useState } from "react";
import { api, dataBR, formatarBytes, json, type Perfil, type RegistroAuditoria, type Usuario } from "../api/client";
import { useAuth } from "../auth";
import { Alerta } from "../components/Alerta";

interface Resumo {
  documentos_total: number; arquivos_total: number; armazenamento_bytes: number; usuarios_ativos: number;
  documentos_por_status: Record<string, number>; documentos_por_tipo: Record<string, number>;
  documentos_por_classificacao: Record<string, number>; usuarios_por_perfil: Record<string, number>;
  ultimas_acoes: RegistroAuditoria[];
}

function Barras({ titulo, dados }: { titulo: string; dados: Record<string, number> }) {
  const max = Math.max(1, ...Object.values(dados));
  const linhas = Object.entries(dados).sort((a, b) => b[1] - a[1]);
  return (
    <figure className="barras">
      <figcaption>{titulo}</figcaption>
      {linhas.length ? (
        <table>
          <tbody>
            {linhas.map(([k, v]) => (
              <tr key={k}><th scope="row">{k}</th>
                <td><span className="barra" style={{ width: `${(v / max) * 100}%` }} aria-hidden="true" /><span className="valor">{v}</span></td></tr>
            ))}
          </tbody>
        </table>
      ) : <p className="vazio">Sem dados</p>}
    </figure>
  );
}

function Usuarios() {
  const [lista, setLista] = useState<Usuario[]>([]);
  const [novo, setNovo] = useState({ nome: "", email: "", senha: "", perfil: "CONSULTA" as Perfil });
  const [erro, setErro] = useState("");
  const [ok, setOk] = useState("");
  const carregar = useCallback(() => { api<Usuario[]>("/api/usuarios").then(setLista).catch((e) => setErro(e.message)); }, []);
  useEffect(carregar, [carregar]);
  async function criar(e: React.FormEvent) {
    e.preventDefault(); setErro(""); setOk("");
    try { await api("/api/usuarios", { method: "POST", body: json(novo) }); setOk("Usuário criado."); setNovo({ nome: "", email: "", senha: "", perfil: "CONSULTA" }); carregar(); }
    catch (err) { setErro((err as Error).message); }
  }
  async function alternar(u: Usuario) {
    try { await api(`/api/usuarios/${u.id}`, { method: "PATCH", body: json({ ativo: !u.ativo }) }); carregar(); }
    catch (err) { setErro((err as Error).message); }
  }
  return (
    <section aria-labelledby="titulo-usuarios">
      <h2 id="titulo-usuarios">Usuários</h2>
      <div className="tabela-rolagem"><table>
        <thead><tr><th scope="col">Nome</th><th scope="col">E-mail</th><th scope="col">Perfil</th><th scope="col">Situação</th><th scope="col">Ação</th></tr></thead>
        <tbody>{lista.map((u) => (
          <tr key={u.id}><td>{u.nome}</td><td>{u.email}</td><td>{u.perfil}</td><td>{u.ativo ? "Ativo" : "Inativo"}</td>
            <td><button type="button" onClick={() => alternar(u)}>{u.ativo ? "Desativar" : "Reativar"}</button></td></tr>))}
        </tbody></table></div>
      <form onSubmit={criar} className="form-grade" aria-label="Novo usuário">
        <div><label htmlFor="un">Nome</label><input id="un" value={novo.nome} onChange={(e) => setNovo({ ...novo, nome: e.target.value })} /></div>
        <div><label htmlFor="ue">E-mail</label><input id="ue" type="email" value={novo.email} onChange={(e) => setNovo({ ...novo, email: e.target.value })} /></div>
        <div><label htmlFor="us">Senha inicial</label><input id="us" type="password" autoComplete="new-password" value={novo.senha} onChange={(e) => setNovo({ ...novo, senha: e.target.value })} /></div>
        <div><label htmlFor="up">Perfil</label><select id="up" value={novo.perfil} onChange={(e) => setNovo({ ...novo, perfil: e.target.value as Perfil })}>
          <option>CONSULTA</option><option>OPERADOR</option><option>GESTOR</option><option>ADMIN</option></select></div>
        <div className="largo"><Alerta>{erro}</Alerta><Alerta tipo="sucesso">{ok}</Alerta><button type="submit">Criar usuário</button></div>
      </form>
    </section>
  );
}

export function Painel() {
  const { pode } = useAuth();
  const [r, setR] = useState<Resumo | null>(null);
  const [erro, setErro] = useState("");
  useEffect(() => { api<Resumo>("/api/painel/resumo").then(setR).catch((e) => setErro(e.message)); }, []);
  if (erro) return <Alerta>{erro}</Alerta>;
  if (!r) return <p aria-busy="true">Carregando…</p>;
  return (
    <section>
      <h1>Painel administrativo</h1>
      <div className="indicadores">
        <div className="indicador"><span className="numero">{r.documentos_total}</span><span>documentos</span></div>
        <div className="indicador"><span className="numero">{r.arquivos_total}</span><span>arquivos PDF</span></div>
        <div className="indicador"><span className="numero">{formatarBytes(r.armazenamento_bytes)}</span><span>armazenados</span></div>
        <div className="indicador"><span className="numero">{r.usuarios_ativos}</span><span>usuários ativos</span></div>
      </div>
      <div className="grade-barras">
        <Barras titulo="Por status" dados={r.documentos_por_status} />
        <Barras titulo="Por tipo" dados={r.documentos_por_tipo} />
        <Barras titulo="Por classificação" dados={r.documentos_por_classificacao} />
        <Barras titulo="Usuários por perfil" dados={r.usuarios_por_perfil} />
      </div>
      <h2>Últimas ações</h2>
      <ul className="acoes">{r.ultimas_acoes.map((a) => <li key={a.id}><time>{dataBR(a.momento)}</time> — {a.acao} ({a.recurso} {a.recurso_id})</li>)}</ul>
      {pode("usuario:gerenciar") && <Usuarios />}
    </section>
  );
}
