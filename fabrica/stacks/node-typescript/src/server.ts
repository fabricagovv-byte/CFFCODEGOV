import { criarServidor } from "./app.ts";
const porta = Number(process.env.PORT ?? 8000);
criarServidor().listen(porta, () => console.log(`API em http://localhost:${porta}`));
