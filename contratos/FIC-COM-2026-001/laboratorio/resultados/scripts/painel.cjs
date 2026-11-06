const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1366, height: 860 } }); const e = [];
 p.on('pageerror', x => e.push(x.message)); await p.goto('http://127.0.0.1:8777/'); await p.waitForTimeout(1500);
 const stats = await p.$eval('#stats', x => x.innerText.replace(/\s+/g, ' ').trim()); const n = await p.$$eval('#tasks .line', x => x.length);
 await p.screenshot({ path: process.argv[2] }); console.log(JSON.stringify({ erros: e, stats, tarefas_na_tela: n })); await b.close(); })();
