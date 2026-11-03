// MOD-007 — Cliente HTTP: tratamento de erros e utilitários.
import { afterEach, describe, expect, it, vi } from "vitest";
import { api, ApiError, formatarBytes, qs, token } from "./client";

afterEach(() => { vi.restoreAllMocks(); token.limpar(); });

function resposta(status: number, corpo: unknown) {
  return new Response(JSON.stringify(corpo), { status, headers: { "content-type": "application/json" } });
}

describe("api", () => {
  it("envia o token e retorna JSON", async () => {
    token.definir("abc");
    const f = vi.spyOn(globalThis, "fetch").mockResolvedValue(resposta(200, { ok: true }));
    await expect(api("/api/x")).resolves.toEqual({ ok: true });
    expect(new Headers(f.mock.calls[0][1]!.headers).get("Authorization")).toBe("Bearer abc");
  });
  it("converte detail do FastAPI em mensagem", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(resposta(422, { detail: [{ loc: ["body", "titulo"], msg: "obrigatório" }] }));
    await expect(api("/api/x")).rejects.toThrow("titulo: obrigatório");
  });
  it("limpa a sessão em 401", async () => {
    token.definir("expirado");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(resposta(401, { detail: "Token inválido ou expirado" }));
    await expect(api("/api/x")).rejects.toBeInstanceOf(ApiError);
    expect(token.obter()).toBeNull();
  });
  it("informa falta de conexão", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("network"));
    await expect(api("/api/x")).rejects.toThrow("Sem conexão com o servidor");
  });
});

describe("utilitários", () => {
  it("qs ignora vazios", () => { expect(qs({ a: 1, b: "", c: undefined, d: "x y" })).toBe("?a=1&d=x+y"); });
  it("formata bytes", () => { expect(formatarBytes(500)).toBe("500 B"); expect(formatarBytes(2048)).toBe("2.0 KB"); });
});
