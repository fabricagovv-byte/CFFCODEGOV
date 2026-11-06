// Preview real de um sistema gerado pela fábrica: entra com o usuário de demonstração, cria 2 registros
// fictícios em cada cadastro PELA TELA e captura formulário e lista. Não publica nada.
// Uso: node preview_sistema.cjs <URL> <plano.json> <pasta destino> <email> <senha>
"use strict";
const fs = require("fs");
const path = require("path");
let chromium;
try { ({ chromium } = require("playwright")); } catch (e) { console.error("playwright ausente"); process.exit(3); }
const [url, planoArq, destino, email, senha] = process.argv.slice(2);
const plano = JSON.parse(fs.readFileSync(planoArq, "utf8"));
fs.mkdirSync(destino, { recursive: true });
let n = 0;
async function foto(page, nome) {
  n += 1;
  const arq = path.join(destino, `${String(n).padStart(2, "0")}-${nome}.png`);
  await page.screenshot({ path: arq, fullPage: true });
  console.log("captura:", arq);
}
async function preencher(page, campo, valor, i) {
  const el = page.locator(`#${campo.id}`);
  if (campo.tipo === "booleano") { if (valor) await el.check(); return; }
  if (campo.tipo === "enum") { await el.selectOption(String(valor)); return; }
  if (campo.tipo === "referencia") {
    const opcoes = await el.locator("option").evaluateAll((os) => os.map((o) => o.value).filter((v) => v));
    if (opcoes.length) await el.selectOption(opcoes[i % opcoes.length]);
    return;
  }
  if (valor === null || valor === undefined) return;
  await el.fill(String(valor));
}
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  await page.goto(`${url}/login`);
  await page.getByLabel("E-mail").fill(email);
  await page.getByLabel("Senha").fill(senha);
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.waitForLoadState("networkidle");
  await foto(page, "inicio");
  for (const m of plano.modulos) {
    await page.getByRole("link", { name: m.rotulo, exact: true }).click();
    await page.getByRole("heading", { name: m.rotulo, exact: true }).waitFor();
    for (let i = 0; i < 2; i++) {
      await page.getByRole("button", { name: "Novo" }).click();
      for (const c of m.campos) await preencher(page, c, c.valores[i], i);
      if (i === 0) await foto(page, `${m.tabela}-formulario`);
      await page.getByRole("button", { name: "Cadastrar" }).click();
      await page.getByText("Salvo com sucesso.").waitFor({ timeout: 10000 });
    }
    await page.waitForLoadState("networkidle");
    await foto(page, `${m.tabela}-lista`);
  }
  await browser.close();
})().catch((e) => { console.error(e.message || e); process.exit(1); });
