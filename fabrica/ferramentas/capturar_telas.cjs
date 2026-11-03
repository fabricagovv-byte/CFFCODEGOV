// Capturas REAIS de tela para as evidências (Playwright).
// Uso: node fabrica/ferramentas/capturar_telas.cjs <URL> <pasta evidencias/OS> <email> <senha>
const { chromium } = require("playwright");
const fs = require("fs");
const os = require("os");
const path = require("path");

const [url, pasta, email, senha] = process.argv.slice(2);
if (!url || !pasta || !email || !senha) { console.error("uso: <URL> <pasta> <email> <senha>"); process.exit(2); }
const registros = [];

async function foto(page, mod, nome, desc) {
  const dir = path.join(pasta, mod, "SCREENSHOTS");
  fs.mkdirSync(dir, { recursive: true });
  const arq = path.join(dir, nome);
  await page.screenshot({ path: arq, fullPage: true });
  registros.push({ modulo: mod, arquivo: arq, descricao: desc, url: page.url(), em: new Date().toISOString() });
  console.log(`captura: ${arq} — ${desc}`);
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await page.goto(`${url}/login`);
  await page.getByLabel("E-mail").waitFor();
  await foto(page, "MOD-001", "01-login.png", "Tela de login");
  await page.getByLabel("E-mail").fill(email);
  await page.getByLabel("Senha").fill("senha-incorreta");
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.getByRole("alert").waitFor();
  await foto(page, "MOD-001", "02-login-erro.png", "Mensagem de erro com senha incorreta");
  await page.goto(`${url}/esqueci-senha`);
  await foto(page, "MOD-001", "03-recuperar-senha.png", "Tela de recuperação de senha");

  await page.goto(`${url}/login`);
  await page.getByLabel("E-mail").fill(email);
  await page.getByLabel("Senha").fill(senha);
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.getByRole("heading", { name: "Documentos" }).waitFor();
  await page.locator("table").waitFor();
  await foto(page, "MOD-002", "04-documentos-lista.png", "Lista de documentos (dados fictícios)");
  await page.getByRole("button", { name: "Novo documento" }).click();
  await page.getByLabel("Título *").fill("Ofício de teste da captura de evidências");
  await page.getByLabel("Interessado").fill("Secretaria Fictícia de Administração");
  await page.getByLabel("Assunto").fill("Documento criado automaticamente pelo script de evidências.");
  await foto(page, "MOD-002", "05-documento-cadastro.png", "Formulário de cadastro preenchido");
  await page.getByRole("button", { name: "Cadastrar" }).click();
  await page.getByRole("heading", { name: /Ofício de teste da captura/ }).waitFor();
  await foto(page, "MOD-002", "06-documento-detalhe.png", "Documento criado — detalhe e edição");

  const pdf = path.join(os.tmpdir(), "oficio-evidencia.pdf");
  fs.writeFileSync(pdf, "%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n");
  await page.setInputFiles("#arquivo-pdf", pdf);
  await page.getByRole("button", { name: "Enviar" }).click();
  await page.getByText(/enviado\./).waitFor();
  await foto(page, "MOD-003", "07-upload-pdf.png", "PDF anexado com SHA-256 e tamanho");
  fs.writeFileSync(pdf.replace(".pdf", ".txt"), "não sou pdf");
  await page.setInputFiles("#arquivo-pdf", pdf.replace(".pdf", ".txt"));
  await page.getByRole("button", { name: "Enviar" }).click();
  await page.getByRole("alert").waitFor();
  await foto(page, "MOD-003", "08-upload-rejeitado.png", "Arquivo não-PDF rejeitado");

  await page.goto(`${url}/pesquisa`);
  await page.getByRole("searchbox").fill("ofício");
  await page.getByRole("button", { name: "Pesquisar" }).click();
  await page.getByText(/resultado\(s\)/).waitFor();
  await foto(page, "MOD-004", "09-pesquisa.png", "Pesquisa por 'ofício'");

  await page.goto(`${url}/painel`);
  await page.getByRole("heading", { name: "Painel administrativo" }).waitFor();
  await foto(page, "MOD-005", "10-painel.png", "Painel com indicadores e usuários");

  await page.goto(`${url}/auditoria`);
  await page.locator("table").waitFor();
  await foto(page, "MOD-006", "11-auditoria.png", "Trilha de auditoria");

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${url}/documentos`);
  await page.locator("table").waitFor();
  await foto(page, "MOD-002", "12-documentos-celular.png", "Lista em tela de celular (390px)");

  await browser.close();
  fs.writeFileSync(path.join(pasta, "CAPTURAS.json"), JSON.stringify({ fonte: "Playwright/Chromium — capturar_telas.cjs", url, capturas: registros }, null, 2));
})().catch((e) => { console.error(e); process.exit(1); });
