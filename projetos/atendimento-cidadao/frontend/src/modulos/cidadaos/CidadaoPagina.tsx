// MOD-102 — Cidadãos: lista, busca, cadastro, edição e exclusão (gerado pela fábrica).
import { useCallback, useEffect, useState } from "react";
import type { Pagina } from "../../api/client";
import { useAuth } from "../../auth";
import { Alerta } from "../../components/Alerta";
import { Paginacao } from "../../components/Paginacao";
import { alterarCidadao, criarCidadao, excluirCidadao, listarCidadao, type Cidadao, type CidadaoDados } from "./api";

const ESCREVER = ["ADMIN", "GESTOR", "OPERADOR"];
const EXCLUIR = ["ADMIN", "GESTOR"];
type Form = Record<keyof CidadaoDados, unknown>;
const VAZIO: Form = { nome: "", cpf: "", email: "", telefone: "", data_nascimento: "" };

export function validarCidadao(d: Form): string | null {
  if (d.nome === "" || d.nome === null || d.nome === undefined) return "Nome é obrigatório";
  if (typeof d.nome === "string" && d.nome.length > 150) return "Nome: máximo de 150 caracteres";
  if (d.cpf === "" || d.cpf === null || d.cpf === undefined) return "CPF é obrigatório";
  if (typeof d.email === "string" && d.email.length > 254) return "E-mail: máximo de 254 caracteres";
  if (d.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(String(d.email))) return "E-mail: e-mail inválido";
  if (typeof d.telefone === "string" && d.telefone.length > 20) return "Telefone: máximo de 20 caracteres";
  return null;
}

function paraEnvio(d: Form): CidadaoDados {
  const saida: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(d)) saida[k] = v === "" ? null : v;
  return saida as unknown as CidadaoDados;
}

export function CidadaoPagina() {
  const { usuario } = useAuth();
  const podeEscrever = !!usuario && ESCREVER.includes(usuario.perfil);
  const podeExcluir = !!usuario && EXCLUIR.includes(usuario.perfil);
  const [res, setRes] = useState<Pagina<Cidadao> | null>(null);
  const [q, setQ] = useState("");
  const [pagina, setPagina] = useState(1);
  const [form, setForm] = useState<Form | null>(null);
  const [editando, setEditando] = useState<number | null>(null);
  const [erro, setErro] = useState("");
  const [ok, setOk] = useState("");

  const carregar = useCallback(() => { listarCidadao(q, pagina).then(setRes).catch((e) => setErro(e.message)); }, [q, pagina]);
  useEffect(carregar, [carregar]);

  async function salvar(e: React.FormEvent) {
    e.preventDefault(); setErro(""); setOk("");
    if (!form) return;
    const problema = validarCidadao(form);
    if (problema) { setErro(problema); return; }
    try {
      if (editando) await alterarCidadao(editando, paraEnvio(form)); else await criarCidadao(paraEnvio(form));
      setOk("Salvo com sucesso."); setForm(null); setEditando(null); carregar();
    } catch (err) { setErro((err as Error).message); }
  }

  async function excluir(item: Cidadao) {
    if (!window.confirm("Excluir este registro? Ele ficará inativo.")) return;
    try { await excluirCidadao(item.id); setOk("Registro excluído."); carregar(); } catch (err) { setErro((err as Error).message); }
  }

  const set = (k: string, v: unknown) => setForm((f) => ({ ...(f as Form), [k]: v }));

  return (
    <section>
      <div className="cabecalho-secao">
        <h1>Cidadãos</h1>
        {podeEscrever && !form && <button type="button" onClick={() => { setForm({ ...VAZIO }); setEditando(null); }}>Novo</button>}
      </div>
      <form role="search" className="form-grade" onSubmit={(e) => { e.preventDefault(); setPagina(1); carregar(); }}>
        <div className="largo"><label htmlFor="busca-cidadaos">Pesquisar</label>
          <input id="busca-cidadaos" type="search" value={q} onChange={(e) => setQ(e.target.value)} maxLength={200} /></div>
      </form>
      {form && (
        <form onSubmit={salvar} className="form-grade" aria-label="Dados de Cidadãos">
          <div><label htmlFor="cidadaos-nome">Nome *</label><input id="cidadaos-nome" type="text" maxLength={150} value={(form.nome ?? "") as string} onChange={(e) => set("nome", e.target.value)} /></div>
          <div><label htmlFor="cidadaos-cpf">CPF *</label><input id="cidadaos-cpf" type="text" value={(form.cpf ?? "") as string} onChange={(e) => set("cpf", e.target.value)} /></div>
          <div><label htmlFor="cidadaos-email">E-mail</label><input id="cidadaos-email" type="email" maxLength={254} value={(form.email ?? "") as string} onChange={(e) => set("email", e.target.value)} /></div>
          <div><label htmlFor="cidadaos-telefone">Telefone</label><input id="cidadaos-telefone" type="text" maxLength={20} value={(form.telefone ?? "") as string} onChange={(e) => set("telefone", e.target.value)} /></div>
          <div><label htmlFor="cidadaos-data_nascimento">Data de nascimento</label><input id="cidadaos-data_nascimento" type="date" value={(form.data_nascimento ?? "") as string} onChange={(e) => set("data_nascimento", e.target.value)} /></div>
          <div className="largo"><button type="submit">{editando ? "Salvar alterações" : "Cadastrar"}</button>
            {" "}<button type="button" onClick={() => { setForm(null); setEditando(null); }}>Cancelar</button></div>
        </form>
      )}
      <Alerta>{erro}</Alerta>
      <Alerta tipo="sucesso">{ok}</Alerta>
      {res && (<>
        <div className="tabela-rolagem"><table>
          <caption className="sr-only">Cidadãos</caption>
          <thead><tr><th scope="col">Nome</th><th scope="col">CPF</th><th scope="col">E-mail</th><th scope="col">Telefone</th><th scope="col">Data de nascimento</th><th scope="col">Ações</th></tr></thead>
          <tbody>{res.itens.map((x) => (
            <tr key={x.id}><td>{String(x.nome ?? "—")}</td><td>{String(x.cpf ?? "—")}</td><td>{String(x.email ?? "—")}</td><td>{String(x.telefone ?? "—")}</td><td>{String(x.data_nascimento ?? "—")}</td><td>{podeEscrever && <button type="button" onClick={() => { const { id, ativo, criado_em, atualizado_em, ...d } = x; void id; void ativo; void criado_em; void atualizado_em; setForm(d as Form); setEditando(x.id); }}>Editar</button>}{" "}{podeExcluir && <button type="button" onClick={() => excluir(x)}>Excluir</button>}</td></tr>
          ))}</tbody>
        </table></div>
        {res.itens.length === 0 && <p className="vazio">Nenhum registro.</p>}
        <Paginacao pagina={res.pagina} total={res.total} porPagina={res.por_pagina} aoMudar={setPagina} />
      </>)}
    </section>
  );
}
