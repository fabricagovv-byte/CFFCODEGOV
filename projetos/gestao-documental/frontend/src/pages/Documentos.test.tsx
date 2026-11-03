// MOD-002 — Formulário de documento: validação no cliente.
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { expect, it, vi } from "vitest";
import { AuthProvider } from "../auth";
import { FormDocumento } from "./FormDocumento";

it("bloqueia título curto e envia dados válidos", async () => {
  const salvar = vi.fn().mockResolvedValue(undefined);
  render(<MemoryRouter><AuthProvider><FormDocumento aoSalvar={salvar} rotulo="Cadastrar" /></AuthProvider></MemoryRouter>);
  await userEvent.type(screen.getByLabelText("Título *"), "ab");
  await userEvent.click(screen.getByRole("button", { name: "Cadastrar" }));
  expect((await screen.findByRole("alert")).textContent).toContain("pelo menos 3");
  expect(salvar).not.toHaveBeenCalled();
  await userEvent.type(screen.getByLabelText("Título *"), "c Ofício");
  await userEvent.click(screen.getByRole("button", { name: "Cadastrar" }));
  expect(salvar).toHaveBeenCalledWith(expect.objectContaining({ titulo: "abc Ofício", classificacao: "PUBLICO" }));
});
