// MOD-004 — Pesquisa: envia termos e filtros na query string.
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, it, vi } from "vitest";
import { Pesquisa } from "./Pesquisa";

afterEach(() => vi.restoreAllMocks());

it("monta a consulta com termos e mostra o total", async () => {
  const f = vi.spyOn(globalThis, "fetch").mockImplementation(async (url) => new Response(
    JSON.stringify(String(url).includes("/tipos") ? ["Ofício"] : { total: 0, pagina: 1, por_pagina: 20, itens: [] }),
    { status: 200, headers: { "content-type": "application/json" } }));
  render(<MemoryRouter><Pesquisa /></MemoryRouter>);
  await userEvent.type(screen.getByRole("searchbox"), "merenda escolar");
  await userEvent.click(screen.getByRole("button", { name: "Pesquisar" }));
  expect(await screen.findByText("0 resultado(s)")).toBeTruthy();
  expect(f.mock.calls.some(([u]) => String(u).includes("q=merenda+escolar"))).toBe(true);
});
