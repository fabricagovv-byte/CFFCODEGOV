// Capturas REAIS das telas da OS-TESTE-002 (Interessados e Protocolos), criando registros pela interface.
// Uso: node contratos/TESTE-002/capturar_telas_teste002.cjs <URL> <pasta evidencias/OS> <email> <senha>
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const [url, pasta, email, senha] = process.argv.slice(2);
const reg = [];
async function foto(page, mod, nome, desc) {
  const dir = path.join(pasta, mod, "SCREENSHOTS"); fs.mkdirSync(dir, { recursive: true });
  const arq = path.join(dir, nome); await page.screenshot({ path: arq, fullPage: true });
  reg.push({ modulo: mod, arquivo: arq, descricao: desc, em: new Date().toISOString() }); console.log("captura:", arq);
}
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  await page.goto(`${url}/login`);
  await page.getByLabel("E-mail").fill(email); await page.getByLabel("Senha").fill(senha);
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.getByRole("heading", { name: "Documentos" }).waitFor();
  // MOD-101 Interessados
  await page.getByRole("link", { name: "Interessados" }).click();
  await page.getByRole("heading", { name: "Interessados" }).waitFor();
  await page.getByRole("button", { name: "Novo" }).click();
  await page.getByLabel("Nome *").fill("Maria Cidadã Exemplo");
  await page.getByLabel("CPF/CNPJ *").fill("111.111.111-11");
  await page.getByLabel("E-mail").fill("maria.exemplo@exemplo.gov.br");
  await page.getByRole("button", { name: "Cadastrar" }).click();
  await page.getByRole("alert").waitFor();
  await foto(page, "MOD-101", "01-validacao-cpf-invalido.png", "CPF inválido recusado pelo servidor");
  await page.getByLabel("CPF/CNPJ *").fill("529.982.247-25");
  await page.getByRole("button", { name: "Cadastrar" }).click();
  await page.getByText("Salvo com sucesso.").waitFor();
  await page.getByRole("button", { name: "Novo" }).click();
  await page.getByLabel("Nome *").fill("Empresa Exemplo Ltda");
  await page.getByLabel("CPF/CNPJ *").fill("11.222.333/0001-81");
  await page.getByLabel("Tipo de pessoa *").selectOption("JURIDICA");
  await page.getByRole("button", { name: "Cadastrar" }).click();
  await page.getByText("Salvo com sucesso.").waitFor();
  await foto(page, "MOD-101", "02-interessados-lista.png", "Dois interessados cadastrados pela tela");
  // MOD-102 Protocolos
  await page.getByRole("link", { name: "Protocolos" }).click();
  await page.getByRole("heading", { name: "Protocolos" }).waitFor();
  await page.getByRole("button", { name: "Novo" }).click();
  await page.getByLabel("Número *").fill("2026/000123");
  await page.getByLabel("Assunto *").fill("Solicitação de alvará de funcionamento");
  await page.getByLabel("Interessado *").selectOption({ label: "Empresa Exemplo Ltda" });
  await page.getByLabel("Canal *").selectOption("PORTAL");
  await page.getByLabel("Prazo").fill("2026-11-30");
  await page.getByLabel("Valor da taxa (R$)").fill("150.75");
  await page.getByLabel("Quantidade de folhas").fill("12");
  await foto(page, "MOD-102", "01-protocolo-formulario.png", "Formulário de protocolo com relacionamento ao interessado");
  await page.getByRole("button", { name: "Cadastrar" }).click();
  await page.getByText("Salvo com sucesso.").waitFor();
  await page.getByRole("searchbox").fill("alvará");
  await page.waitForTimeout(600);
  await foto(page, "MOD-102", "02-protocolos-busca.png", "Busca por 'alvará' na lista de protocolos");
  await page.goto(`${url}/auditoria`); await page.locator("table").waitFor();
  await foto(page, "MOD-102", "03-auditoria-modulos.png", "Auditoria registrando INTERESSADOS_CRIADO e PROTOCOLOS_CRIADO");
  await browser.close();
  fs.writeFileSync(path.join(pasta, "CAPTURAS.json"), JSON.stringify({ fonte: "Playwright/Chromium", url, capturas: reg }, null, 2));
})().catch((e) => { console.error(e); process.exit(1); });
