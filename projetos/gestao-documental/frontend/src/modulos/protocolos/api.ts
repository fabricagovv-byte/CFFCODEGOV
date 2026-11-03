// MOD-102 — Protocolos: cliente da API (gerado pela fábrica).
import { api, json, qs, type Pagina } from "../../api/client";

export interface Protocolo {
  id: number;
  numero: string;
  assunto: string;
  interessado_id: number;
  canal: "PRESENCIAL" | "EMAIL" | "PORTAL" | "TELEFONE";
  prioridade: "NORMAL" | "URGENTE";
  prazo: string | null;
  valor_taxa: string | null;
  quantidade_folhas: number | null;
  sigiloso: boolean | null;
  ativo: boolean;
  criado_em: string;
  atualizado_em: string;
}

export type ProtocoloDados = Omit<Protocolo, "id" | "ativo" | "criado_em" | "atualizado_em">;

export const listarProtocolo = (q = "", pagina = 1) => api<Pagina<Protocolo>>(`/api/protocolos${qs({ q, pagina, por_pagina: 20 })}`);
export const criarProtocolo = (d: ProtocoloDados) => api<Protocolo>("/api/protocolos", { method: "POST", body: json(d) });
export const alterarProtocolo = (id: number, d: Partial<ProtocoloDados>) => api<Protocolo>(`/api/protocolos/${id}`, { method: "PATCH", body: json(d) });
export const excluirProtocolo = (id: number) => api<void>(`/api/protocolos/${id}`, { method: "DELETE" });
