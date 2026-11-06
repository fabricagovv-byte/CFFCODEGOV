// MOD-102 — Cidadãos: cliente da API (gerado pela fábrica).
import { api, json, qs, type Pagina } from "../../api/client";

export interface Cidadao {
  id: number;
  nome: string;
  cpf: string;
  email: string | null;
  telefone: string | null;
  data_nascimento: string | null;
  ativo: boolean;
  criado_em: string;
  atualizado_em: string;
}

export type CidadaoDados = Omit<Cidadao, "id" | "ativo" | "criado_em" | "atualizado_em">;

export const listarCidadao = (q = "", pagina = 1) => api<Pagina<Cidadao>>(`/api/cidadaos${qs({ q, pagina, por_pagina: 20 })}`);
export const criarCidadao = (d: CidadaoDados) => api<Cidadao>("/api/cidadaos", { method: "POST", body: json(d) });
export const alterarCidadao = (id: number, d: Partial<CidadaoDados>) => api<Cidadao>(`/api/cidadaos/${id}`, { method: "PATCH", body: json(d) });
export const excluirCidadao = (id: number) => api<void>(`/api/cidadaos/${id}`, { method: "DELETE" });
