'use strict';

// Estado da tela: sessão do usuário e visão aberta.
const estado = { token: lerToken(), visao: 'overview', usuario: null };

const el = (id) => document.getElementById(id);

const TITULOS = {
  overview: 'Visão geral',
  channels: 'Canais de comunicação',
  posts: 'Publicações institucionais',
  campaigns: 'Campanhas editoriais',
  contacts: 'Contatos e consentimentos',
  tickets: 'Atendimento e chamados',
  audit: 'Trilha de auditoria',
};

// Quem pode criar registros em cada visão (o servidor confere de novo).
const PODE_CRIAR = ['ADMIN', 'EDITOR'];
const PODE_APROVAR = ['ADMIN', 'APPROVER'];

const CADASTROS = {
  channels: {
    caminho: '/api/channels',
    campos: [
      { nome: 'name', rotulo: 'Nome do canal', tipo: 'text' },
      { nome: 'description', rotulo: 'Descrição', tipo: 'text' },
    ],
    colunas: ['name', 'description'],
  },
  posts: {
    caminho: '/api/posts',
    campos: [
      { nome: 'channel_id', rotulo: 'ID do canal', tipo: 'number' },
      { nome: 'title', rotulo: 'Título', tipo: 'text' },
      { nome: 'body', rotulo: 'Conteúdo', tipo: 'textarea' },
    ],
    colunas: ['title', 'channel', 'status'],
  },
  campaigns: {
    caminho: '/api/campaigns',
    campos: [
      { nome: 'name', rotulo: 'Nome da campanha', tipo: 'text' },
      { nome: 'objective', rotulo: 'Objetivo', tipo: 'textarea' },
      { nome: 'channel_id', rotulo: 'ID do canal (opcional)', tipo: 'number', opcional: true },
    ],
    colunas: ['name', 'objective', 'status'],
  },
  contacts: {
    caminho: '/api/contacts',
    campos: [
      { nome: 'name', rotulo: 'Nome', tipo: 'text' },
      { nome: 'email', rotulo: 'E-mail', tipo: 'email', opcional: true },
      { nome: 'category', rotulo: 'Categoria', tipo: 'text' },
      { nome: 'consent', rotulo: 'Consentimento expresso', tipo: 'checkbox' },
    ],
    colunas: ['name', 'email', 'consent'],
  },
  tickets: {
    caminho: '/api/tickets',
    campos: [
      { nome: 'subject', rotulo: 'Assunto', tipo: 'text' },
      { nome: 'description', rotulo: 'Descrição', tipo: 'textarea' },
      { nome: 'priority', rotulo: 'Prioridade', tipo: 'select', opcoes: ['BAIXA', 'NORMAL', 'ALTA'], padrao: 'NORMAL' },
    ],
    colunas: ['subject', 'priority', 'status'],
  },
};

function lerToken() {
  try {
    return sessionStorage.getItem('dg_token');
  } catch {
    return null;
  }
}

function guardarToken(token) {
  try {
    if (token) sessionStorage.setItem('dg_token', token);
    else sessionStorage.removeItem('dg_token');
  } catch {
    /* navegador sem armazenamento de sessão: segue só na memória */
  }
}

function mensagemDeErro(detalhe) {
  if (Array.isArray(detalhe)) {
    return detalhe.map((item) => String(item.msg || '').replace(/^Value error, /, '')).join('; ');
  }
  return detalhe;
}

async function api(caminho, metodo = 'GET', corpo) {
  const resposta = await fetch(caminho, {
    method: metodo,
    headers: { Authorization: 'Bearer ' + (estado.token || ''), 'Content-Type': 'application/json' },
    body: corpo ? JSON.stringify(corpo) : undefined,
  });
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(mensagemDeErro(dados.detail) || 'Erro ' + resposta.status);
  return dados;
}

function avisar(texto, erro = false) {
  const aviso = el('notice');
  aviso.hidden = false;
  aviso.className = 'notice' + (erro ? ' error' : '');
  aviso.textContent = texto;
  setTimeout(() => { aviso.hidden = true; }, 5500);
}

function criar(tag, atributos = {}, ...filhos) {
  const elemento = document.createElement(tag);
  for (const [nome, valor] of Object.entries(atributos)) {
    if (nome === 'texto') elemento.textContent = valor;
    else if (nome === 'classe') elemento.className = valor;
    else elemento.setAttribute(nome, valor);
  }
  elemento.append(...filhos);
  return elemento;
}

function temPerfil(perfis) {
  return Boolean(estado.usuario) && perfis.includes(estado.usuario.role);
}

function mostrarLogin() {
  el('loginPane').hidden = false;
  el('content').hidden = true;
}

async function atualizar() {
  if (!estado.token) return mostrarLogin();
  try {
    estado.usuario = await api('/api/me');
  } catch {
    guardarToken(null);
    estado.token = null;
    return mostrarLogin();
  }
  el('loginPane').hidden = true;
  el('content').hidden = false;
  el('identity').textContent = `${estado.usuario.name} • ${estado.usuario.role}`;
  el('pageTitle').textContent = TITULOS[estado.visao];
  document.querySelectorAll('.nav button').forEach((botao) => {
    botao.classList.toggle('active', botao.dataset.view === estado.visao);
  });
  const { kpis } = await api('/api/overview');
  const indicadores = [
    ['Canais', kpis.channels],
    ['Publicações', kpis.posts],
    ['Publicadas', kpis.posts_published],
    ['Chamados em aberto', kpis.tickets_open],
  ];
  el('summary').replaceChildren(...indicadores.map(([rotulo, valor]) =>
    criar('div', { classe: 'kpi' }, criar('div', { classe: 'num', texto: String(valor) }), criar('div', { classe: 'lbl', texto: rotulo }))));
  await desenharVisao();
}

async function desenharVisao() {
  const visao = estado.visao;
  if (visao === 'overview') return desenharVisaoGeral();
  if (visao === 'audit') {
    const eventos = await api('/api/audit');
    el('sectionTitle').textContent = 'Últimos 200 eventos';
    el('formWrap').replaceChildren(criar('p', { classe: 'hint', texto: 'Registro de todas as ações feitas na plataforma.' }));
    return listar(eventos, ['action', 'entity', 'at']);
  }
  const cadastro = CADASTROS[visao];
  const itens = await api(cadastro.caminho);
  el('sectionTitle').textContent = `${TITULOS[visao]} (${itens.length})`;
  listar(itens, cadastro.colunas);
  desenharFormulario(cadastro);
}

async function desenharVisaoGeral() {
  const caminhos = [['Canais', '/api/channels'], ['Publicações', '/api/posts'], ['Campanhas', '/api/campaigns'], ['Chamados', '/api/tickets']];
  const totais = await Promise.all(caminhos.map(([, caminho]) => api(caminho)));
  el('sectionTitle').textContent = 'Atividade registrada';
  el('tableWrap').replaceChildren(...caminhos.map(([rotulo], i) =>
    criar('div', { classe: 'gridrow' }, criar('strong', { texto: rotulo }), criar('span', { texto: String(totais[i].length) }),
      criar('span', { classe: 'state', texto: 'registros no banco' }))));
  el('formWrap').replaceChildren(criar('p', {
    classe: 'hint',
    texto: 'Use o menu para cadastrar canais, criar publicações com aprovação por outra pessoa e acompanhar o atendimento.',
  }));
}

function campoDoFormulario(campo) {
  if (campo.tipo === 'checkbox') {
    return criar('label', {}, criar('input', { type: 'checkbox', name: campo.nome, id: 'campo-' + campo.nome, classe: 'check' }), ' ' + campo.rotulo);
  }
  let entrada;
  if (campo.tipo === 'textarea') {
    entrada = criar('textarea', { name: campo.nome, id: 'campo-' + campo.nome });
  } else if (campo.tipo === 'select') {
    entrada = criar('select', { name: campo.nome, id: 'campo-' + campo.nome },
      ...campo.opcoes.map((opcao) => criar('option', { texto: opcao })));
    entrada.value = campo.padrao;
  } else {
    entrada = criar('input', { name: campo.nome, id: 'campo-' + campo.nome, type: campo.tipo });
  }
  if (!campo.opcional && campo.tipo !== 'select') entrada.required = true;
  return criar('label', {}, campo.rotulo, entrada);
}

function desenharFormulario(cadastro) {
  if (!temPerfil(PODE_CRIAR)) {
    el('formWrap').replaceChildren(criar('p', { classe: 'hint', texto: 'Seu perfil permite consultar, sem criar registros.' }));
    return;
  }
  const formulario = criar('form', { id: 'createForm' }, ...cadastro.campos.map(campoDoFormulario),
    criar('button', { type: 'submit', texto: 'Criar registro' }));
  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    const dados = {};
    for (const campo of cadastro.campos) {
      const entrada = formulario.elements[campo.nome];
      let valor = entrada.value;
      if (campo.tipo === 'checkbox') valor = entrada.checked;
      else if (campo.tipo === 'number') valor = entrada.value ? Number(entrada.value) : null;
      if (valor !== '' && valor !== null) dados[campo.nome] = valor;
    }
    try {
      await api(cadastro.caminho, 'POST', dados);
      avisar('Registro salvo');
      await atualizar();
    } catch (erro) {
      avisar(erro.message, true);
    }
  });
  el('formWrap').replaceChildren(formulario);
}

function botoesDeAcao(item) {
  const acoes = [];
  if (estado.visao === 'posts') {
    if (temPerfil(PODE_CRIAR) && item.status === 'RASCUNHO') acoes.push(['submit', 'Enviar para revisão']);
    if (temPerfil(PODE_APROVAR) && item.status === 'EM_REVISAO') acoes.push(['approve', 'Aprovar']);
    if (temPerfil(PODE_APROVAR) && item.status === 'APROVADO') acoes.push(['publish', 'Publicar']);
  }
  if (estado.visao === 'tickets' && temPerfil(PODE_CRIAR) && item.status !== 'RESOLVIDO') acoes.push(['resolve', 'Resolver']);
  return acoes.map(([acao, rotulo]) => {
    const botao = criar('button', { type: 'button', texto: rotulo });
    botao.addEventListener('click', () => executarAcao(acao, item.id));
    return botao;
  });
}

async function executarAcao(acao, id) {
  try {
    if (acao === 'resolve') await api(`/api/tickets/${id}/status`, 'PATCH', { status: 'RESOLVIDO' });
    else await api(`/api/posts/${id}/${acao}`, 'POST');
    avisar('Ação registrada');
    await atualizar();
  } catch (erro) {
    avisar(erro.message, true);
  }
}

function listar(itens, colunas) {
  if (!itens.length) {
    el('tableWrap').replaceChildren(criar('div', { classe: 'empty', texto: 'Nenhum registro ainda.' }));
    return;
  }
  const texto = (valor) => String(valor ?? '');
  const situacaoTexto = (item) => (estado.visao === 'contacts'
    ? (item.consent ? 'Com consentimento' : 'Sem consentimento')
    : texto(item[colunas[2]]));
  el('tableWrap').replaceChildren(...itens.slice(0, 80).map((item) => {
    const acoes = botoesDeAcao(item);
    const situacao = criar('span', { classe: 'state', texto: situacaoTexto(item) });
    if (acoes.length) situacao.append(criar('br'), ...acoes);
    return criar('div', { classe: 'gridrow' },
      criar('div', {}, criar('strong', { texto: texto(item[colunas[0]]) }), criar('small', { texto: '#' + item.id })),
      criar('span', { texto: texto(item[colunas[1]]) }),
      situacao);
  }));
}

function ligarEventos() {
  const falhou = (erro) => avisar(erro.message, true);
  document.querySelectorAll('.nav button').forEach((botao) => {
    botao.addEventListener('click', () => {
      estado.visao = botao.dataset.view;
      atualizar().catch(falhou);
    });
  });
  el('reload').addEventListener('click', () => atualizar().catch(falhou));
  el('logout').addEventListener('click', async () => {
    try {
      await api('/api/logout', 'POST');
    } catch {
      /* sessão já encerrada no servidor */
    }
    guardarToken(null);
    estado.token = null;
    estado.usuario = null;
    atualizar();
  });
  el('loginForm').addEventListener('submit', async (evento) => {
    evento.preventDefault();
    try {
      const resposta = await api('/api/login', 'POST', {
        username: evento.target.username.value,
        password: evento.target.password.value,
      });
      estado.token = resposta.token;
      guardarToken(resposta.token);
      await atualizar();
    } catch (erro) {
      avisar(erro.message, true);
    }
  });
}

ligarEventos();
atualizar().catch((erro) => avisar(erro.message, true));
setInterval(() => {
  if (estado.token && estado.visao === 'overview') atualizar().catch(() => {});
}, 20000);
