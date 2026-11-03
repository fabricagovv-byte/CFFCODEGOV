// MOD-001 — Contexto de autenticação.
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api, definirAoExpirar, json, token, type Perfil, type Usuario } from "./api/client";

const PERMISSOES: Record<Perfil, string[]> = {
  ADMIN: ["doc:criar", "doc:editar", "doc:arquivar", "arquivo:enviar", "painel:ler", "auditoria:ler", "usuario:gerenciar"],
  GESTOR: ["doc:criar", "doc:editar", "doc:arquivar", "arquivo:enviar", "painel:ler", "auditoria:ler"],
  OPERADOR: ["doc:criar", "doc:editar", "arquivo:enviar"],
  CONSULTA: [],
};

interface Ctx {
  usuario: Usuario | null; carregando: boolean;
  entrar: (email: string, senha: string) => Promise<void>; sair: () => Promise<void>;
  pode: (permissao: string) => boolean;
}
const AuthCtx = createContext<Ctx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    definirAoExpirar(() => setUsuario(null));
    if (!token.obter()) { setCarregando(false); return; }
    api<Usuario>("/api/auth/me").then(setUsuario).catch(() => token.limpar()).finally(() => setCarregando(false));
  }, []);

  const entrar = useCallback(async (email: string, senha: string) => {
    const r = await api<{ access_token: string; usuario: Usuario }>("/api/auth/login", { method: "POST", body: json({ email, senha }) });
    token.definir(r.access_token);
    setUsuario(r.usuario);
  }, []);

  const sair = useCallback(async () => {
    try { await api("/api/auth/logout", { method: "POST" }); } catch { /* sessão já expirada */ }
    token.limpar();
    setUsuario(null);
  }, []);

  const pode = useCallback((p: string) => !!usuario && PERMISSOES[usuario.perfil].includes(p), [usuario]);
  const valor = useMemo(() => ({ usuario, carregando, entrar, sair, pode }), [usuario, carregando, entrar, sair, pode]);
  return <AuthCtx.Provider value={valor}>{children}</AuthCtx.Provider>;
}

export function useAuth(): Ctx {
  const c = useContext(AuthCtx);
  if (!c) throw new Error("useAuth fora do AuthProvider");
  return c;
}
