// MOD-001 — Redefinição de senha por token.
import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, json } from "../api/client";
import { Alerta } from "../components/Alerta";

export function RedefinirSenha() {
  const [params] = useSearchParams();
  const [senha, setSenha] = useState("");
  const [conf, setConf] = useState("");
  const [erro, setErro] = useState("");
  const [ok, setOk] = useState(false);
  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setErro("");
    if (senha !== conf) { setErro("As senhas não conferem"); return; }
    try {
      await api("/api/auth/redefinir-senha", { method: "POST", body: json({ token: params.get("token") ?? "", nova_senha: senha }) });
      setOk(true);
    } catch (err) { setErro((err as Error).message); }
  }
  return (
    <main id="conteudo" className="cartao-login">
      <h1>Definir nova senha</h1>
      {ok ? <Alerta tipo="sucesso">Senha alterada. <Link to="/login">Entrar</Link></Alerta> : (
        <form onSubmit={enviar}>
          <label htmlFor="nova">Nova senha (mín. 10 caracteres, letras e números)</label>
          <input id="nova" type="password" autoComplete="new-password" value={senha} onChange={(e) => setSenha(e.target.value)} />
          <label htmlFor="conf">Confirme a nova senha</label>
          <input id="conf" type="password" autoComplete="new-password" value={conf} onChange={(e) => setConf(e.target.value)} />
          <Alerta>{erro}</Alerta>
          <button type="submit">Salvar</button>
        </form>
      )}
    </main>
  );
}
