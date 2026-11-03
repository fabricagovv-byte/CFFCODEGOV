// MOD-007/MOD-001 — Cliente HTTP com token, tratamento de erros e tipos.
export type Perfil = "ADMIN" | "GESTOR" | "OPERADOR" | "CONSULTA";
export type Classificacao = "PUBLICO" | "RESTRITO" | "SIGILOSO";
export type StatusDoc = "RASCUNHO" | "ATIVO" | "ARQUIVADO";

export interface Usuario { id: number; nome: string; email: string; perfil: Perfil; ativo: boolean }
export interface Arquivo { id: number; nome_original: string; tamanho: number; sha256: string; enviado_em: string }
export interface Documento {
  id: number; numero: string; titulo: string; tipo: string; assunto: string; interessado: string;
  classificacao: Classificacao; status: StatusDoc; criado_em: string; atualizado_em: string; arquivos: Arquivo[];
}
export interface Pagina<T> { total: number; pagina: number; por_pagina: number; itens: T[] }
export interface RegistroAuditoria {
  id: number; momento: string; usuario_id: number | null; acao: string; recurso: string;
  recurso_id: string; ip: string; detalhes: string;
}

const CHAVE = "gd.token";

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

export const token = {
  obter: (): string | null => { try { return sessionStorage.getItem(CHAVE); } catch { return null; } },
  definir: (t: string) => { try { sessionStorage.setItem(CHAVE, t); } catch { /* sem armazenamento */ } },
  limpar: () => { try { sessionStorage.removeItem(CHAVE); } catch { /* sem armazenamento */ } },
};

function mensagemDeErro(status: number, corpo: unknown): string {
  const det = (corpo as { detail?: unknown })?.detail;
  if (typeof det === "string") return det;
  if (Array.isArray(det) && det.length) {
    return det.map((d: { loc?: unknown[]; msg?: string }) => `${(d.loc ?? []).slice(1).join(".")}: ${d.msg}`).join("; ");
  }
  if (status === 0) return "Sem conexão com o servidor";
  return `Erro ${status}`;
}

export let aoExpirarSessao: () => void = () => {};
export function definirAoExpirar(fn: () => void) { aoExpirarSessao = fn; }

export async function api<T>(caminho: string, opcoes: RequestInit = {}): Promise<T> {
  const headers = new Headers(opcoes.headers);
  const t = token.obter();
  if (t) headers.set("Authorization", `Bearer ${t}`);
  if (opcoes.body && !(opcoes.body instanceof FormData)) headers.set("Content-Type", "application/json");
  let resp: Response;
  try {
    resp = await fetch(caminho, { ...opcoes, headers });
  } catch {
    throw new ApiError(0, mensagemDeErro(0, null));
  }
  if (resp.status === 204) return undefined as T;
  const tipo = resp.headers.get("content-type") ?? "";
  const corpo = tipo.includes("application/json") ? await resp.json() : await resp.blob();
  if (!resp.ok) {
    if (resp.status === 401 && t) { token.limpar(); aoExpirarSessao(); }
    throw new ApiError(resp.status, mensagemDeErro(resp.status, corpo));
  }
  return corpo as T;
}

export const json = (dados: unknown) => JSON.stringify(dados);

export function qs(params: Record<string, string | number | undefined | null>): string {
  const u = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== "") u.set(k, String(v)); });
  const s = u.toString();
  return s ? `?${s}` : "";
}

export async function baixarArquivo(a: Arquivo) {
  const blob = await api<Blob>(`/api/arquivos/${a.id}`);
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url; link.download = a.nome_original; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function formatarBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 ** 2) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 ** 2).toFixed(1)} MB`;
}

export const dataBR = (iso: string) => new Date(iso).toLocaleString("pt-BR");
