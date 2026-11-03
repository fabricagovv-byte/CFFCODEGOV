// MOD-006 — Auditoria: lista registros somente leitura.
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, it, vi } from "vitest";
import { Auditoria } from "./Auditoria";

afterEach(() => vi.restoreAllMocks());

it("lista registros e não oferece botões de edição", async () => {
  const pagina = { total: 1, pagina: 1, por_pagina: 50, itens: [{ id: 1, momento: "2026-11-03T12:00:00Z", usuario_id: 2, acao: "LOGIN", recurso: "auth", recurso_id: "2", ip: "127.0.0.1", detalhes: "{}" }] };
  vi.spyOn(globalThis, "fetch").mockImplementation(async (url) => new Response(
    JSON.stringify(String(url).includes("/acoes") ? ["LOGIN"] : pagina), { status: 200, headers: { "content-type": "application/json" } }));
  render(<MemoryRouter><Auditoria /></MemoryRouter>);
  expect(await screen.findByRole("cell", { name: "LOGIN" })).toBeTruthy();
  expect(screen.queryByRole("button", { name: /excluir|editar/i })).toBeNull();
});
