// MOD-001 — Tela de login.
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { Alerta } from "../components/Alerta";

export function Login() {
  const { entrar } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setErro("");
    if (!email || !senha) { setErro("Informe e-mail e senha"); return; }
    setEnviando(true);
    try {
      await entrar(email, senha);
      nav("/documentos");
    } catch (err) {
      setErro((err as Error).message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main id="conteudo" className="cartao-login">
      <h1>Gestão Documental Pública</h1>
      <p className="subtitulo">Ambiente de demonstração — dados fictícios</p>
      <form onSubmit={enviar} noValidate>
        <label htmlFor="email">E-mail</label>
        <input id="email" type="email" autoComplete="username" value={email} onChange={(e) => setEmail(e.target.value)} />
        <label htmlFor="senha">Senha</label>
        <input id="senha" type="password" autoComplete="current-password" value={senha} onChange={(e) => setSenha(e.target.value)} />
        <Alerta>{erro}</Alerta>
        <button type="submit" disabled={enviando}>{enviando ? "Entrando…" : "Entrar"}</button>
      </form>
      <p><Link to="/esqueci-senha">Esqueci minha senha</Link></p>
    </main>
  );
}
