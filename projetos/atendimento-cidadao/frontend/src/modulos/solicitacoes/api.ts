// MOD-103 — Solicitações: cliente da API (gerado pela fábrica).
import { api, json, qs, type Pagina } from "../../api/client";

export interface Solicitacao {
  id: number;
  protocolo: string;
  cidadao_id: number;
  unidade_id: number;
  canal: "PRESENCIAL" | "PORTAL" | "TELEFONE" | "WHATSAPP";
  assunto: string;
  descricao: string | null;
  situacao: "ABERTA" | "EM_ATENDIMENTO" | "CONCLUIDA" | "CANCELADA";
  prazo: string | null;
  prioritaria: boolean | null;
  ativo: boolean;
  criado_em: string;
  atualizado_em: string;
}

export type SolicitacaoDados = Omit<Solicitacao, "id" | "ativo" | "criado_em" | "atualizado_em">;

export const listarSolicitacao = (q = "", pagina = 1) => api<Pagina<Solicitacao>>(`/api/solicitacoes${qs({ q, pagina, por_pagina: 20 })}`);
export const criarSolicitacao = (d: SolicitacaoDados) => api<Solicitacao>("/api/solicitacoes", { method: "POST", body: json(d) });
export const alterarSolicitacao = (id: number, d: Partial<SolicitacaoDados>) => api<Solicitacao>(`/api/solicitacoes/${id}`, { method: "PATCH", body: json(d) });
export const excluirSolicitacao = (id: number) => api<void>(`/api/solicitacoes/${id}`, { method: "DELETE" });
