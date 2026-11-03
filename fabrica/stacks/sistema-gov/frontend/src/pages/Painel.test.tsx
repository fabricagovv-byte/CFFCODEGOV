// MOD-005 — Painel: renderiza indicadores vindos da API.
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, it, vi } from "vitest";
import { AuthProvider } from "../auth";
import { Painel } from "./Painel";

afterEach(() => vi.restoreAllMocks());

it("mostra totais e barras", async () => {
  const resumo = { documentos_total: 7, arquivos_total: 3, armazenamento_bytes: 2048, usuarios_ativos: 4,
    documentos_por_status: { ATIVO: 6, ARQUIVADO: 1 }, documentos_por_tipo: { "Ofício": 7 },
    documentos_por_classificacao: { PUBLICO: 7 }, usuarios_por_perfil: { ADMIN: 1 }, ultimas_acoes: [] };
  vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify(resumo), { status: 200, headers: { "content-type": "application/json" } }));
  render(<MemoryRouter><AuthProvider><Painel /></AuthProvider></MemoryRouter>);
  expect((await screen.findAllByText("7")).length).toBeGreaterThanOrEqual(1);
  expect(screen.getByText("documentos")).toBeTruthy();
  expect(screen.getByText("2.0 KB")).toBeTruthy();
  expect(screen.getByText("Por status")).toBeTruthy();
});
