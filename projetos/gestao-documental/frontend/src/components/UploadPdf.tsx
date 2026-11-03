// MOD-003 — Envio de PDF com validação no cliente (o servidor valida de novo).
import { useRef, useState } from "react";
import { api, type Arquivo } from "../api/client";
import { Alerta } from "./Alerta";

export const LIMITE_MB = 20;

export function validarPdf(f: File | undefined, limiteMb = LIMITE_MB): string | null {
  if (!f) return "Selecione um arquivo";
  if (!f.name.toLowerCase().endsWith(".pdf")) return "Somente arquivos .pdf são aceitos";
  if (f.size === 0) return "Arquivo vazio";
  if (f.size > limiteMb * 1024 * 1024) return `Arquivo excede o limite de ${limiteMb} MB`;
  return null;
}

export function UploadPdf({ documentoId, aoEnviar }: { documentoId: number; aoEnviar: (a: Arquivo) => void }) {
  const ref = useRef<HTMLInputElement>(null);
  const [erro, setErro] = useState("");
  const [ok, setOk] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setErro(""); setOk("");
    const f = ref.current?.files?.[0];
    const problema = validarPdf(f);
    if (problema) { setErro(problema); return; }
    const fd = new FormData();
    fd.append("arquivo", f!);
    setEnviando(true);
    try {
      const a = await api<Arquivo>(`/api/documentos/${documentoId}/arquivos`, { method: "POST", body: fd });
      setOk(`Arquivo "${a.nome_original}" enviado.`);
      if (ref.current) ref.current.value = "";
      aoEnviar(a);
    } catch (err) {
      setErro((err as Error).message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={enviar} className="upload" aria-label="Enviar PDF">
      <label htmlFor="arquivo-pdf">Anexar PDF (até {LIMITE_MB} MB)</label>
      <input id="arquivo-pdf" ref={ref} type="file" accept="application/pdf,.pdf" />
      <button type="submit" disabled={enviando}>{enviando ? "Enviando…" : "Enviar"}</button>
      <Alerta>{erro}</Alerta>
      <Alerta tipo="sucesso">{ok}</Alerta>
    </form>
  );
}
