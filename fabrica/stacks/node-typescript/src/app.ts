import { createServer, type Server } from "node:http";

export function criarServidor(): Server {
  return createServer((req, res) => {
    if (req.method === "GET" && req.url === "/api/health") {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ status: "ok", sistema: "{{NOME}}" }));
      return;
    }
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ erro: "não encontrado" }));
  });
}
