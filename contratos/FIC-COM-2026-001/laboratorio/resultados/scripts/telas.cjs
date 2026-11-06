const { chromium } = require('playwright');
(async () => {
  const out = process.argv[2]; const b = await chromium.launch(); const errs = {};
  const page = await b.newPage({ viewport: { width: 1366, height: 860 } });
  const track = k => { errs[k] = []; page.removeAllListeners('pageerror'); page.on('pageerror', e => errs[k].push(e.message)); };
  track('fabrica'); await page.goto('http://127.0.0.1:8777/'); await page.waitForTimeout(1500);
  errs.fabrica_stats = await page.$eval('#stats', e => e.innerText.trim().slice(0, 200));
  await page.screenshot({ path: out + '/01_fabrica_painel.png', fullPage: false });
  track('comunicacao'); await page.goto('http://127.0.0.1:8765/'); await page.waitForTimeout(800);
  await page.screenshot({ path: out + '/02_comunicacao_login.png' });
  await page.fill('input[name=username]', 'revisor'); await page.fill('input[name=password]', 'demo-revisor-senha-forte-2026');
  await page.click('#loginForm button'); await page.waitForTimeout(1200);
  await page.screenshot({ path: out + '/03_comunicacao_visao_geral.png' });
  for (const [v, n] of [['posts', '04_publicacoes'], ['tickets', '05_chamados'], ['audit', '06_auditoria']]) {
    await page.click(`.nav button[data-view=${v}]`); await page.waitForTimeout(900); await page.screenshot({ path: `${out}/${n}.png` });
  }
  console.log(JSON.stringify(errs, null, 1)); await b.close();
})();
