// MOD-101 — Unidades: cliente da API (gerado pela fábrica).
import { api, json, qs, type Pagina } from "../../api/client";

export interface Unidade {
  id: number;
  nome: string;
  sigla: string;
  municipio: string;
  telefone: string | null;
  ativo: boolean;
  criado_em: string;
  atualizado_em: string;
}

export type UnidadeDados = Omit<Unidade, "id" | "ativo" | "criado_em" | "atualizado_em">;

export const listarUnidade = (q = "", pagina = 1) => api<Pagina<Unidade>>(`/api/unidades${qs({ q, pagina, por_pagina: 20 })}`);
export const criarUnidade = (d: UnidadeDados) => api<Unidade>("/api/unidades", { method: "POST", body: json(d) });
export const alterarUnidade = (id: number, d: Partial<UnidadeDados>) => api<Unidade>(`/api/unidades/${id}`, { method: "PATCH", body: json(d) });
export const excluirUnidade = (id: number) => api<void>(`/api/unidades/${id}`, { method: "DELETE" });
