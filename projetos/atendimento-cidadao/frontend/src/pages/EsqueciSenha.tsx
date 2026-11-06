// MOD-001 — Solicitação de recuperação de senha.
import { useState } from "react";
import { Link } from "react-router-dom";
import { api, json } from "../api/client";
import { Alerta } from "../components/Alerta";

export function EsqueciSenha() {
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState("");
  const [erro, setErro] = useState("");
  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setErro(""); setMsg("");
    try {
      const r = await api<{ mensagem: string }>("/api/auth/recuperar-senha", { method: "POST", body: json({ email }) });
      setMsg(r.mensagem);
    } catch (err) { setErro((err as Error).message); }
  }
  return (
    <main id="conteudo" className="cartao-login">
      <h1>Recuperar senha</h1>
      <form onSubmit={enviar}>
        <label htmlFor="email-rec">E-mail cadastrado</label>
        <input id="email-rec" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        <Alerta>{erro}</Alerta>
        <Alerta tipo="sucesso">{msg}</Alerta>
        <button type="submit">Enviar instruções</button>
      </form>
      <p><Link to="/login">Voltar ao login</Link></p>
    </main>
  );
}
