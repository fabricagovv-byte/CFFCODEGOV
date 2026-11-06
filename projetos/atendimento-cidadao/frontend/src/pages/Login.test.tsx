// MOD-001 — Tela de login.
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, it, vi } from "vitest";
import { AuthProvider } from "../auth";
import { Login } from "./Login";

afterEach(() => vi.restoreAllMocks());

const montar = () => render(<MemoryRouter><AuthProvider><Login /></AuthProvider></MemoryRouter>);

it("tem campos rotulados e acessíveis", () => {
  montar();
  expect(screen.getByLabelText("E-mail")).toBeTruthy();
  expect(screen.getByLabelText("Senha")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Entrar" })).toBeTruthy();
});

it("valida campos vazios sem chamar a API", async () => {
  const f = vi.spyOn(globalThis, "fetch");
  montar();
  await userEvent.click(screen.getByRole("button", { name: "Entrar" }));
  expect((await screen.findByRole("alert")).textContent).toContain("Informe e-mail e senha");
  expect(f).not.toHaveBeenCalled();
});

it("exibe a mensagem de erro do servidor", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({ detail: "E-mail ou senha inválidos" }), { status: 401, headers: { "content-type": "application/json" } }));
  montar();
  await userEvent.type(screen.getByLabelText("E-mail"), "a@b.gov.br");
  await userEvent.type(screen.getByLabelText("Senha"), "errada");
  await userEvent.click(screen.getByRole("button", { name: "Entrar" }));
  expect((await screen.findByRole("alert")).textContent).toContain("E-mail ou senha inválidos");
});
