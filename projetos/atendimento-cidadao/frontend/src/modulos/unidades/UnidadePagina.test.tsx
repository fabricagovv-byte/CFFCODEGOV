// MOD-101 — testes da tela de Unidades (gerados pela fábrica).
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, it, vi } from "vitest";
import { AuthProvider } from "../../auth";
import { UnidadePagina, validarUnidade } from "./UnidadePagina";

afterEach(() => vi.restoreAllMocks());

const ITEM = {"id": 1, "ativo": true, "criado_em": "2026-01-01T00:00:00Z", "atualizado_em": "2026-01-01T00:00:00Z", "nome": "Nome de teste 0", "sigla": "Sigla de teste 0", "municipio": "Município de teste 0", "telefone": "Telefone de teste 0"};

function mockApi() {
  return vi.spyOn(globalThis, "fetch").mockImplementation(async () => new Response(
    JSON.stringify({ total: 1, pagina: 1, por_pagina: 20, itens: [ITEM] }), { status: 200, headers: { "content-type": "application/json" } }));
}

it("lista os registros vindos da API", async () => {
  mockApi();
  render(<MemoryRouter><AuthProvider><UnidadePagina /></AuthProvider></MemoryRouter>);
  expect(await screen.findByText(String(ITEM.nome))).toBeTruthy();
  expect(screen.getByRole("heading", { name: "Unidades" })).toBeTruthy();
});

it("pesquisa envia o termo para a API", async () => {
  const f = mockApi();
  render(<MemoryRouter><AuthProvider><UnidadePagina /></AuthProvider></MemoryRouter>);
  await userEvent.type(screen.getByRole("searchbox"), "abc{Enter}");
  expect(f.mock.calls.some(([u]) => String(u).includes("/api/unidades") && String(u).includes("q=abc"))).toBe(true);
});

it("valida campo obrigatório", () => {
  const d = { ...ITEM } as Record<string, unknown>; d.nome = "";
  expect(validarUnidade(d as never)).toMatch(/obrigatório/);
  expect(validarUnidade(ITEM as never)).toBeNull();
});
