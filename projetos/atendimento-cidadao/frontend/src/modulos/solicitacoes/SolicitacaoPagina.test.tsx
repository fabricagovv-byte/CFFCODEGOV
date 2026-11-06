// MOD-103 — testes da tela de Solicitações (gerados pela fábrica).
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, it, vi } from "vitest";
import { AuthProvider } from "../../auth";
import { SolicitacaoPagina, validarSolicitacao } from "./SolicitacaoPagina";

afterEach(() => vi.restoreAllMocks());

const ITEM = {"id": 1, "ativo": true, "criado_em": "2026-01-01T00:00:00Z", "atualizado_em": "2026-01-01T00:00:00Z", "protocolo": "Protocolo de teste 0", "cidadao_id": 1, "unidade_id": 1, "canal": "PRESENCIAL", "assunto": "Assunto de teste 0", "descricao": "Descrição de teste 0", "situacao": "ABERTA", "prazo": "2026-01-10", "prioritaria": true};

function mockApi() {
  return vi.spyOn(globalThis, "fetch").mockImplementation(async () => new Response(
    JSON.stringify({ total: 1, pagina: 1, por_pagina: 20, itens: [ITEM] }), { status: 200, headers: { "content-type": "application/json" } }));
}

it("lista os registros vindos da API", async () => {
  mockApi();
  render(<MemoryRouter><AuthProvider><SolicitacaoPagina /></AuthProvider></MemoryRouter>);
  expect(await screen.findByText(String(ITEM.protocolo))).toBeTruthy();
  expect(screen.getByRole("heading", { name: "Solicitações" })).toBeTruthy();
});

it("pesquisa envia o termo para a API", async () => {
  const f = mockApi();
  render(<MemoryRouter><AuthProvider><SolicitacaoPagina /></AuthProvider></MemoryRouter>);
  await userEvent.type(screen.getByRole("searchbox"), "abc{Enter}");
  expect(f.mock.calls.some(([u]) => String(u).includes("/api/solicitacoes") && String(u).includes("q=abc"))).toBe(true);
});

it("valida campo obrigatório", () => {
  const d = { ...ITEM } as Record<string, unknown>; d.protocolo = "";
  expect(validarSolicitacao(d as never)).toMatch(/obrigatório/);
  expect(validarSolicitacao(ITEM as never)).toBeNull();
});
