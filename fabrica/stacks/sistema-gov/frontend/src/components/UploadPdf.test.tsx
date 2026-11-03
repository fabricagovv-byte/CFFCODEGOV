// MOD-003 — Validação de PDF no cliente.
import { describe, expect, it } from "vitest";
import { validarPdf } from "./UploadPdf";

const arq = (nome: string, bytes: number) => new File([new Uint8Array(bytes)], nome, { type: "application/pdf" });

describe("validarPdf", () => {
  it("aceita PDF dentro do limite", () => expect(validarPdf(arq("a.pdf", 10))).toBeNull());
  it("exige arquivo", () => expect(validarPdf(undefined)).toMatch(/Selecione/));
  it("rejeita extensão", () => expect(validarPdf(arq("a.docx", 10))).toMatch(/\.pdf/));
  it("rejeita vazio", () => expect(validarPdf(arq("a.pdf", 0))).toMatch(/vazio/));
  it("rejeita acima do limite", () => expect(validarPdf(arq("a.pdf", 2 * 1024 * 1024), 1)).toMatch(/limite/));
});
