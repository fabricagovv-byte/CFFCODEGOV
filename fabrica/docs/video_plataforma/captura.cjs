// Captura quadro a quadro: node captura.cjs <html> <pasta> <fps> [t1,t2,... para amostra]
const { chromium } = require("playwright");
const path = require("path"), fs = require("fs");
(async () => {
  const [html, pasta, fpsS, amostra] = process.argv.slice(2);
  const fps = Number(fpsS);
  fs.mkdirSync(pasta, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
  const erros = [];
  p.on("console", (m) => { if (m.type() === "error") erros.push(m.text()); });
  p.on("pageerror", (e) => erros.push(String(e)));
  await p.goto("file://" + path.resolve(html) + "?rec=1");
  await p.evaluate(() => document.fonts.ready);
  await p.waitForFunction(() => [].every.call(document.images, (i) => i.complete && i.naturalWidth > 0));
  const dur = await p.evaluate(() => window.DURACAO);
  const tempos = amostra ? amostra.split(",").map(Number) : Array.from({ length: Math.round(dur * fps) }, (_, i) => i / fps);
  let n = 0;
  for (const t of tempos) {
    await p.evaluate((x) => window.seek(x), t);
    const nome = amostra ? `t${String(t).replace(".", "_")}.png` : `f${String(n).padStart(5, "0")}.jpg`;
    await p.screenshot(amostra ? { path: path.join(pasta, nome) } : { path: path.join(pasta, nome), type: "jpeg", quality: 93 });
    n++;
  }
  console.log("quadros:", n, "duracao:", dur, "erros:", erros.length ? erros : "nenhum");
  await b.close();
})().catch((e) => { console.error("FALHOU:", e.message); process.exit(1); });
