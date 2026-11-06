// Capturas reais da OS-FIC-002 (dados DEMO). Uso: node telas_os002.cjs <pasta_saida>
const { chromium } = require('playwright');
const C = 'http://127.0.0.1:8765', F = 'http://127.0.0.1:8777', out = process.argv[2];
const senha = u => `demo-${u}-senha-forte-2026`;
async function api(path, method = 'GET', body, tok) {
  const r = await fetch(C + path, { method, headers: { 'Content-Type': 'application/json', ...(tok ? { Authorization: 'Bearer ' + tok } : {}) }, body: body ? JSON.stringify(body) : undefined });
  return { status: r.status, json: await r.json().catch(() => ({})) };
}
(async () => {
  const res = {}; const tok = async u => (await api('/api/login', 'POST', { username: u, password: senha(u) })).json.token;
  const ed = await tok('editor'), rv = await tok('revisor');
  const ch = (await api('/api/channels', 'POST', { name: 'Boletim interno DEMO' }, ed)).json.id;
  for (const est of ['RASCUNHO', 'EM_REVISAO', 'PUBLICADO']) {
    const id = (await api('/api/posts', 'POST', { channel_id: ch, title: `Circular ${est} DEMO`, body: 'Conteúdo de teste DEMO' }, ed)).json.id;
    if (est !== 'RASCUNHO') await api(`/api/posts/${id}/submit`, 'POST', null, ed);
    if (est === 'PUBLICADO') { await api(`/api/posts/${id}/approve`, 'POST', null, rv); await api(`/api/posts/${id}/publish`, 'POST', null, rv); }
  }
  const ct = (await api('/api/contacts', 'POST', { name: 'Pessoa DEMO', email: 'pessoa@exemplo.gov.br', consent: true }, ed)).json.id;
  await api('/api/tickets', 'POST', { subject: 'Dúvida sobre circular DEMO', description: 'Texto com dado pessoal DEMO', contact_id: ct }, ed);
  res.chamado_contato_inexistente = (await api('/api/tickets', 'POST', { subject: 'Teste DEMO', description: 'contato 9999', contact_id: 9999 }, ed)).status;
  res.campanha_canal_inexistente = (await api('/api/campaigns', 'POST', { name: 'Camp DEMO', objective: 'Teste', channel_id: 9999 }, ed)).status;
  res.email_invalido = (await api('/api/contacts', 'POST', { name: 'Fulano', email: 'isto-nao-e-email' }, ed)).status;

  const b = await chromium.launch(); const erros = [];
  const pg = await b.newPage({ viewport: { width: 1366, height: 860 } }); pg.on('pageerror', e => erros.push(e.message));
  const entrar = async u => { await pg.goto(C); await pg.waitForTimeout(500); await pg.fill('input[name=username]', u); await pg.fill('input[name=password]', senha(u)); await pg.click('#loginForm button'); await pg.waitForTimeout(1000); };
  // MOD-001: sair revoga a sessão no servidor
  await entrar('editor'); const tokTela = await pg.evaluate(() => sessionStorage.getItem('dg_token'));
  await pg.click('#logout'); await pg.waitForTimeout(800);
  res.token_apos_sair = (await api('/api/me', 'GET', null, tokTela)).status;
  await pg.screenshot({ path: `${out}/MOD-001_01_apos_sair.png` });
  // MOD-001: bloqueio por tentativas
  for (let i = 0; i < 5; i++) { await pg.fill('input[name=username]', 'admin'); await pg.fill('input[name=password]', 'senha-errada-' + i + 'xxxx'); await pg.click('#loginForm button'); await pg.waitForTimeout(300); }
  await pg.fill('input[name=username]', 'admin'); await pg.fill('input[name=password]', senha('admin')); await pg.click('#loginForm button'); await pg.waitForTimeout(500);
  res.mensagem_bloqueio = await pg.$eval('#notice', e => e.textContent);
  await pg.screenshot({ path: `${out}/MOD-001_02_bloqueio_tentativas.png` });
  // MOD-002: leitor vê só publicadas e chamados sem dados pessoais
  await entrar('leitor'); await pg.click('.nav button[data-view=posts]'); await pg.waitForTimeout(800);
  res.leitor_posts_na_tela = await pg.$$eval('#tableWrap .gridrow', x => x.map(e => e.innerText.split('\n')[0]));
  await pg.screenshot({ path: `${out}/MOD-002_01_leitor_so_publicadas.png` });
  await pg.click('.nav button[data-view=tickets]'); await pg.waitForTimeout(800);
  await pg.screenshot({ path: `${out}/MOD-002_02_leitor_chamados.png` });
  await pg.click('#logout'); await pg.waitForTimeout(500);
  // MOD-002: e-mail inválido recusado na tela
  await entrar('editor'); await pg.click('.nav button[data-view=contacts]'); await pg.waitForTimeout(700);
  await pg.fill('#createForm input[name=name]', 'Fulano DEMO'); await pg.fill('#createForm input[name=email]', 'isto@nao'); await pg.fill('#createForm input[name=category]', 'PUBLICO');
  await pg.evaluate(() => { document.querySelector('#createForm input[name=email]').type = 'text'; });
  await pg.click('#createForm button'); await pg.waitForTimeout(600);
  res.mensagem_email = await pg.$eval('#notice', e => e.textContent);
  await pg.screenshot({ path: `${out}/MOD-002_03_email_invalido.png` });
  // MOD-003: cabeçalhos de segurança, sem erro de CSP no console
  const r = await pg.goto(C); res.csp_comunicacao = r.headers()['content-security-policy'];
  // MOD-004: painel da fábrica pede chave
  const pf = await b.newPage({ viewport: { width: 1366, height: 860 } }); pf.on('pageerror', e => erros.push('fabrica: ' + e.message));
  await pf.goto(F); await pf.waitForTimeout(800); await pf.screenshot({ path: `${out}/MOD-004_01_pede_chave.png` });
  await pf.fill('#chave', 'x'.repeat(40)); await pf.click('#loginForm button'); await pf.waitForTimeout(800);
  res.fabrica_chave_errada = await pf.$eval('#loginErro', e => e.textContent);
  await pf.screenshot({ path: `${out}/MOD-004_02_chave_errada.png` });
  await pf.fill('#chave', process.env.DG_FACTORY_TOKEN); await pf.click('#loginForm button'); await pf.waitForTimeout(1200);
  res.fabrica_painel = await pf.$eval('#stats', e => e.innerText.replace(/\s+/g, ' ').trim());
  res.fabrica_tarefas = await pf.$$eval('#tasks .line', x => x.length);
  await pf.screenshot({ path: `${out}/MOD-004_03_painel_com_chave.png` });
  res.erros_javascript = erros; console.log(JSON.stringify(res, null, 1)); await b.close();
})();
