// MOD-002 — Formulário de documento (cadastro e edição).
import { useState } from "react";
import type { Classificacao, StatusDoc } from "../api/client";
import { useAuth } from "../auth";
import { Alerta } from "../components/Alerta";

export interface DadosDocumento { titulo: string; tipo: string; assunto: string; interessado: string; classificacao: Classificacao; status: StatusDoc }
const VAZIO: DadosDocumento = { titulo: "", tipo: "Ofício", assunto: "", interessado: "", classificacao: "PUBLICO", status: "ATIVO" };
const TIPOS = ["Ofício", "Memorando", "Portaria", "Decreto", "Contrato", "Parecer", "Requerimento", "Ata"];

export function FormDocumento({ inicial, aoSalvar, rotulo }: { inicial?: Partial<DadosDocumento>; aoSalvar: (d: DadosDocumento) => Promise<void>; rotulo: string }) {
  const { usuario } = useAuth();
  const [d, setD] = useState<DadosDocumento>({ ...VAZIO, ...inicial });
  const [erro, setErro] = useState("");
  const [ok, setOk] = useState("");
  const set = (k: keyof DadosDocumento) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => setD({ ...d, [k]: e.target.value });
  const podeSigiloso = usuario?.perfil === "ADMIN" || usuario?.perfil === "GESTOR";

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setErro(""); setOk("");
    if (d.titulo.trim().length < 3) { setErro("Título deve ter pelo menos 3 caracteres"); return; }
    try { await aoSalvar(d); setOk("Salvo com sucesso."); } catch (err) { setErro((err as Error).message); }
  }

  return (
    <form onSubmit={enviar} className="form-grade" aria-label="Dados do documento">
      <div><label htmlFor="titulo">Título *</label><input id="titulo" value={d.titulo} onChange={set("titulo")} maxLength={300} required /></div>
      <div><label htmlFor="tipo">Tipo *</label>
        <select id="tipo" value={d.tipo} onChange={set("tipo")}>{TIPOS.map((t) => <option key={t}>{t}</option>)}</select></div>
      <div><label htmlFor="interessado">Interessado</label><input id="interessado" value={d.interessado} onChange={set("interessado")} maxLength={200} /></div>
      <div><label htmlFor="classificacao">Classificação (LAI)</label>
        <select id="classificacao" value={d.classificacao} onChange={set("classificacao")}>
          <option value="PUBLICO">Público</option><option value="RESTRITO">Restrito</option>
          {podeSigiloso && <option value="SIGILOSO">Sigiloso</option>}
        </select></div>
      <div><label htmlFor="status">Status</label>
        <select id="status" value={d.status} onChange={set("status")}>
          <option value="ATIVO">Ativo</option><option value="RASCUNHO">Rascunho</option>
          {podeSigiloso && <option value="ARQUIVADO">Arquivado</option>}
        </select></div>
      <div className="largo"><label htmlFor="assunto">Assunto</label><textarea id="assunto" rows={3} value={d.assunto} onChange={set("assunto")} maxLength={5000} /></div>
      <div className="largo"><Alerta>{erro}</Alerta><Alerta tipo="sucesso">{ok}</Alerta><button type="submit">{rotulo}</button></div>
    </form>
  );
}
