// MOD-102 — testes da tela de Protocolos (gerados pela fábrica).
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, it, vi } from "vitest";
import { AuthProvider } from "../../auth";
import { ProtocoloPagina, validarProtocolo } from "./ProtocoloPagina";

afterEach(() => vi.restoreAllMocks());

const ITEM = {"id": 1, "ativo": true, "criado_em": "2026-01-01T00:00:00Z", "atualizado_em": "2026-01-01T00:00:00Z", "numero": "Número de teste 0", "assunto": "Assunto de teste 0", "interessado_id": 1, "canal": "PRESENCIAL", "prioridade": "NORMAL", "prazo": "2026-01-10", "valor_taxa": "10.50", "quantidade_folhas": 1, "sigiloso": true};

function mockApi() {
  return vi.spyOn(globalThis, "fetch").mockImplementation(async () => new Response(
    JSON.stringify({ total: 1, pagina: 1, por_pagina: 20, itens: [ITEM] }), { status: 200, headers: { "content-type": "application/json" } }));
}

it("lista os registros vindos da API", async () => {
  mockApi();
  render(<MemoryRouter><AuthProvider><ProtocoloPagina /></AuthProvider></MemoryRouter>);
  expect(await screen.findByText(String(ITEM.numero))).toBeTruthy();
  expect(screen.getByRole("heading", { name: "Protocolos" })).toBeTruthy();
});

it("pesquisa envia o termo para a API", async () => {
  const f = mockApi();
  render(<MemoryRouter><AuthProvider><ProtocoloPagina /></AuthProvider></MemoryRouter>);
  await userEvent.type(screen.getByRole("searchbox"), "abc{Enter}");
  expect(f.mock.calls.some(([u]) => String(u).includes("/api/protocolos") && String(u).includes("q=abc"))).toBe(true);
});

it("valida campo obrigatório", () => {
  const d = { ...ITEM } as Record<string, unknown>; d.numero = "";
  expect(validarProtocolo(d as never)).toMatch(/obrigatório/);
  expect(validarProtocolo(ITEM as never)).toBeNull();
});
