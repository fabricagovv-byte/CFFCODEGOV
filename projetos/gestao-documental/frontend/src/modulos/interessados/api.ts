// MOD-101 — Interessados: cliente da API (gerado pela fábrica).
import { api, json, qs, type Pagina } from "../../api/client";

export interface Interessado {
  id: number;
  nome: string;
  documento: string;
  tipo_pessoa: "FISICA" | "JURIDICA";
  email: string | null;
  telefone: string | null;
  observacoes: string | null;
  ativo: boolean;
  criado_em: string;
  atualizado_em: string;
}

export type InteressadoDados = Omit<Interessado, "id" | "ativo" | "criado_em" | "atualizado_em">;

export const listarInteressado = (q = "", pagina = 1) => api<Pagina<Interessado>>(`/api/interessados${qs({ q, pagina, por_pagina: 20 })}`);
export const criarInteressado = (d: InteressadoDados) => api<Interessado>("/api/interessados", { method: "POST", body: json(d) });
export const alterarInteressado = (id: number, d: Partial<InteressadoDados>) => api<Interessado>(`/api/interessados/${id}`, { method: "PATCH", body: json(d) });
export const excluirInteressado = (id: number) => api<void>(`/api/interessados/${id}`, { method: "DELETE" });
