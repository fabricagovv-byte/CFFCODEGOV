'use strict';

// ---------------------------------------------------------------- utilidades
const el = (id) => document.getElementById(id);
const estado = { token: lerToken(), usuario: null, tela: 'painel', listas: {} };

function lerToken() {
  try { return sessionStorage.getItem('dg_gerenciador'); } catch { return null; }
}
function guardarToken(token) {
  try { token ? sessionStorage.setItem('dg_gerenciador', token) : sessionStorage.removeItem('dg_gerenciador'); } catch { /* sem armazenamento */ }
}

function h(tag, atributos = {}, ...filhos) {
  const elemento = document.createElement(tag);
  for (const [nome, valor] of Object.entries(atributos)) {
    if (valor === undefined || valor === null || valor === false) continue;
    if (nome === 'texto') elemento.textContent = valor;
    else if (nome === 'classe') elemento.className = valor;
    else if (nome.startsWith('on')) elemento.addEventListener(nome.slice(2), valor);
    else elemento.setAttribute(nome, valor === true ? '' : valor);
  }
  elemento.append(...filhos.flat().filter((f) => f !== null && f !== undefined));
  return elemento;
}

const numero = (v, casas = 2) => (v === null || v === undefined ? '—' : Number(v).toLocaleString('pt-BR', { maximumFractionDigits: casas }));
const reais = (v) => (v === null || v === undefined ? '—' : Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }));
const dataBr = (v) => (v ? v.slice(0, 10).split('-').reverse().join('/') : '—');

function mensagemErro(detalhe, status) {
  if (Array.isArray(detalhe)) return detalhe.map((d) => String(d.msg || '').replace(/^Value error, /, '')).join('; ');
  return detalhe || `Erro ${status}`;
}

async function api(caminho, { metodo = 'GET', corpo, formulario } = {}) {
  const cabecalhos = { Authorization: 'Bearer ' + (estado.token || '') };
  if (corpo !== undefined) cabecalhos['Content-Type'] = 'application/json';
  const resposta = await fetch(caminho, { method: metodo, headers: cabecalhos, body: formulario || (corpo !== undefined ? JSON.stringify(corpo) : undefined) });
  if (resposta.status === 401 && caminho !== '/api/login') { sair(false); throw new Error('Sessão encerrada. Entre de novo.'); }
  if (resposta.status === 204) return null;
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(mensagemErro(dados.detail, resposta.status));
  return dados;
}

async function baixar(caminho, nome) {
  const resposta = await fetch(caminho, { headers: { Authorization: 'Bearer ' + estado.token } });
  if (!resposta.ok) { const d = await resposta.json().catch(() => ({})); return avisar(mensagemErro(d.detail, resposta.status), true); }
  const url = URL.createObjectURL(await resposta.blob());
  const link = h('a', { href: url, download: nome });
  document.body.append(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

function avisar(texto, erro = false) {
  const aviso = el('aviso');
  aviso.hidden = false; aviso.className = erro ? 'erro' : ''; aviso.textContent = texto;
  clearTimeout(avisar.tempo); avisar.tempo = setTimeout(() => { aviso.hidden = true; }, 6000);
}

const podeEscrever = () => ['ADMIN', 'GESTOR'].includes(estado.usuario?.perfil);

function tabela(colunas, linhas) {
  if (!linhas.length) return h('p', { classe: 'nota', texto: 'Nenhum registro.' });
  return h('div', { classe: 'rolagem' }, h('table', {},
    h('thead', {}, h('tr', {}, colunas.map(([rotulo]) => h('th', { texto: rotulo })))),
    h('tbody', {}, linhas.map((linha) => h('tr', {}, colunas.map(([, valor]) => {
      const v = valor(linha);
      return h('td', {}, v instanceof Node ? v : String(v ?? '—'));
    }))))));
}

async function carregarLista(caminho) {
  estado.listas[caminho] = await api(caminho);
  return estado.listas[caminho];
}
const nomePorId = (caminho, id, campo = 'nome') => (estado.listas[caminho] || []).find((x) => x.id === id)?.[campo] ?? (id ? `#${id}` : '—');

// ---------------------------------------------------------------- formulários de cadastro
const OPCOES = {
  esfera: ['', 'FEDERAL', 'ESTADUAL', 'MUNICIPAL', 'DISTRITAL'],
  metrica: ['UST', 'HST', 'PF', 'OUTRA'],
  situacao_contrato: ['ATIVO', 'SUSPENSO', 'ENCERRADO'],
  situacao_agente: ['INTEGRACAO_PENDENTE', 'CONFIGURADO', 'ATIVO', 'INATIVO'],
  situacao_tarefa: ['A_FAZER', 'EM_ANDAMENTO', 'EM_REVISAO', 'CONCLUIDA', 'BLOQUEADA'],
  tipo_evidencia: ['COMMIT', 'TESTE', 'CAPTURA', 'LOG', 'DOCUMENTO', 'OUTRO'],
  situacao_medicao: ['EXECUTADA', 'ACEITA', 'GLOSADA', 'PAGA'],
  integracao: ['PENDENTE', 'CONFIGURADA'],
};

// campo: [nome, rótulo, tipo, opções/lista, obrigatório]
const CADASTROS = {
  orgaos: { titulo: 'Órgãos', caminho: '/api/orgaos', campos: [['nome', 'Nome', 'text', null, true], ['sigla', 'Sigla'], ['cnpj', 'CNPJ (00.000.000/0000-00)'], ['esfera', 'Esfera', 'select', 'esfera'], ['contato', 'Contato']],
    colunas: [['Nome', (x) => x.nome], ['Sigla', (x) => x.sigla], ['Esfera', (x) => x.esfera], ['CNPJ', (x) => x.cnpj]] },
  contratos: { titulo: 'Contratos', caminho: '/api/contratos', listas: ['/api/orgaos'],
    campos: [['orgao_id', 'Órgão', 'ref', '/api/orgaos', true], ['numero', 'Número', 'text', null, true], ['objeto', 'Objeto', 'textarea', null, true], ['metrica', 'Métrica', 'select', 'metrica', true], ['unidade_outra', 'Unidade (se OUTRA)'], ['quantidade_contratada', 'Quantidade contratada', 'number'], ['valor_unitario', 'Valor unitário (R$)', 'number'], ['vigencia_inicio', 'Início da vigência', 'date'], ['vigencia_fim', 'Fim da vigência', 'date'], ['situacao', 'Situação', 'select', 'situacao_contrato']],
    colunas: [['Número', (x) => x.numero], ['Órgão', (x) => nomePorId('/api/orgaos', x.orgao_id)], ['Métrica', (x) => x.metrica], ['Contratado', (x) => numero(x.quantidade_contratada)], ['Vigência', (x) => `${dataBr(x.vigencia_inicio)} a ${dataBr(x.vigencia_fim)}`], ['Situação', (x) => h('span', { classe: 'etq', texto: x.situacao })]] },
  'ordens-servico': { titulo: 'Ordens de serviço', caminho: '/api/ordens-servico', listas: ['/api/contratos'],
    campos: [['contrato_id', 'Contrato', 'ref', '/api/contratos', true, 'numero'], ['numero', 'Número', 'text', null, true], ['descricao', 'Descrição', 'textarea', null, true], ['quantidade', 'Quantidade', 'number'], ['autorizada', 'Autorizada', 'checkbox'], ['autorizado_por', 'Autorizada por (nome e cargo)'], ['autorizado_em', 'Data da autorização', 'date']],
    colunas: [['Número', (x) => x.numero], ['Contrato', (x) => nomePorId('/api/contratos', x.contrato_id, 'numero')], ['Quantidade', (x) => numero(x.quantidade)], ['Autorização', (x) => (x.autorizada ? `${x.autorizado_por} em ${dataBr(x.autorizado_em)}` : h('span', { classe: 'etq PENDENTE', texto: 'Sem autorização' }))]] },
  profissionais: { titulo: 'Profissionais', caminho: '/api/profissionais',
    campos: [['nome', 'Nome', 'text', null, true], ['cargo', 'Cargo', 'text', null, true], ['perfil', 'Perfil'], ['email', 'E-mail', 'email'], ['cpf_mascarado', 'CPF mascarado (***.456.789-**)'], ['ativo', 'Ativo', 'checkbox', null, false, null, true]],
    colunas: [['Nome', (x) => x.nome], ['Cargo', (x) => x.cargo], ['Perfil', (x) => x.perfil], ['CPF', (x) => x.cpf_mascarado], ['Situação', (x) => (x.ativo ? 'Ativo' : 'Inativo')]] },
  agentes: { titulo: 'Agentes', caminho: '/api/agentes', listas: ['/api/projetos', '/api/profissionais'],
    campos: [['codigo', 'Código', 'text', null, true], ['nome', 'Nome', 'text', null, true], ['funcao', 'Função', 'textarea'], ['projeto_id', 'Projeto', 'ref', '/api/projetos', false, 'codigo'], ['profissional_id', 'Profissional responsável', 'ref', '/api/profissionais'], ['situacao', 'Situação', 'select', 'situacao_agente']],
    colunas: [['Código', (x) => x.codigo], ['Nome', (x) => x.nome], ['Projeto', (x) => nomePorId('/api/projetos', x.projeto_id, 'codigo')], ['Responsável', (x) => nomePorId('/api/profissionais', x.profissional_id)], ['Situação', (x) => h('span', { classe: 'etq ' + (x.situacao === 'INTEGRACAO_PENDENTE' ? 'PENDENTE' : 'OK'), texto: x.situacao === 'INTEGRACAO_PENDENTE' ? 'Integração pendente' : x.situacao })]] },
  tarefas: { titulo: 'Tarefas', caminho: '/api/tarefas', listas: ['/api/projetos', '/api/profissionais', '/api/agentes'],
    campos: [['projeto_id', 'Projeto', 'ref', '/api/projetos', true, 'codigo'], ['titulo', 'Título', 'text', null, true], ['descricao', 'Descrição', 'textarea'], ['situacao', 'Situação', 'select', 'situacao_tarefa'], ['profissional_id', 'Profissional', 'ref', '/api/profissionais'], ['agente_id', 'Agente', 'ref', '/api/agentes', false, 'codigo']],
    colunas: [['Tarefa', (x) => x.titulo], ['Projeto', (x) => nomePorId('/api/projetos', x.projeto_id, 'codigo')], ['Profissional', (x) => nomePorId('/api/profissionais', x.profissional_id)], ['Agente', (x) => nomePorId('/api/agentes', x.agente_id, 'codigo')], ['Situação', (x) => h('span', { classe: 'etq', texto: x.situacao })]] },
  evidencias: { titulo: 'Evidências', caminho: '/api/evidencias', listas: ['/api/projetos'],
    campos: [['projeto_id', 'Projeto', 'ref', '/api/projetos', true, 'codigo'], ['tipo', 'Tipo', 'select', 'tipo_evidencia', true], ['descricao', 'Descrição', 'textarea', null, true], ['referencia', 'Referência (commit, link, arquivo)']],
    colunas: [['Data', (x) => dataBr(x.criada_em)], ['Projeto', (x) => nomePorId('/api/projetos', x.projeto_id, 'codigo')], ['Tipo', (x) => x.tipo], ['Descrição', (x) => x.descricao], ['Referência', (x) => x.referencia]] },
  medicoes: { titulo: 'Medições', caminho: '/api/medicoes', listas: ['/api/contratos', '/api/projetos'],
    campos: [['contrato_id', 'Contrato', 'ref', '/api/contratos', true, 'numero'], ['projeto_id', 'Projeto', 'ref', '/api/projetos', false, 'codigo'], ['item', 'Item do catálogo', 'text', null, true], ['descricao', 'O que foi entregue', 'textarea', null, true], ['quantidade', 'Quantidade', 'number', null, true], ['data_execucao', 'Data', 'date', null, true], ['situacao', 'Situação', 'select', 'situacao_medicao'], ['documento_aceite', 'Documento de aceite do órgão'], ['observacao', 'Observação', 'textarea']],
    colunas: [['Data', (x) => dataBr(x.data_execucao)], ['Contrato', (x) => nomePorId('/api/contratos', x.contrato_id, 'numero')], ['Item', (x) => x.item], ['Descrição', (x) => x.descricao], ['Quantidade', (x) => numero(x.quantidade)], ['Situação', (x) => h('span', { classe: 'etq', texto: x.situacao })]] },
};

function campoFormulario([nome, rotulo, tipo = 'text', opcoes, obrigatorio, campoNome = 'nome', padrao]) {
  let entrada;
  if (tipo === 'textarea') entrada = h('textarea', { name: nome, id: 'f-' + nome, required: obrigatorio });
  else if (tipo === 'select') entrada = h('select', { name: nome, id: 'f-' + nome, required: obrigatorio }, OPCOES[opcoes].map((o) => h('option', { value: o, texto: o || '—' })));
  else if (tipo === 'ref') entrada = h('select', { name: nome, id: 'f-' + nome, required: obrigatorio }, h('option', { value: '', texto: '—' }), (estado.listas[opcoes] || []).map((o) => h('option', { value: o.id, texto: o[campoNome] })));
  else if (tipo === 'checkbox') return h('label', {}, h('span', {}, h('input', { type: 'checkbox', name: nome, id: 'f-' + nome, checked: padrao }), ' ' + rotulo));
  else entrada = h('input', { name: nome, id: 'f-' + nome, type: tipo, step: tipo === 'number' ? 'any' : undefined, required: obrigatorio });
  return h('label', {}, rotulo, entrada);
}

function lerFormulario(formulario, campos) {
  const dados = {};
  for (const [nome, , tipo] of campos) {
    const entrada = formulario.elements[nome];
    if (tipo === 'checkbox') { dados[nome] = entrada.checked; continue; }
    if (entrada.value === '') continue;
    dados[nome] = tipo === 'ref' || tipo === 'number' ? Number(entrada.value) : entrada.value;
  }
  return dados;
}

async function telaCadastro(chave) {
  const cfg = CADASTROS[chave];
  await Promise.all((cfg.listas || []).map(carregarLista));
  const itens = await carregarLista(cfg.caminho);
  const blocos = [h('div', { classe: 'bloco' }, h('div', { classe: 'linha-botoes' },
    h('button', { classe: 'secundario', type: 'button', texto: 'Exportar Excel', onclick: () => baixar(`/api/relatorios/exportar/${chave}.xlsx`, `${chave}.xlsx`) })),
  h('h2', { texto: `${cfg.titulo} (${itens.length})` }), tabela(cfg.colunas, itens))];
  if (podeEscrever()) {
    const formulario = h('form', {}, cfg.campos.map(campoFormulario), h('button', { type: 'submit', texto: 'Salvar' }));
    formulario.addEventListener('submit', async (evento) => {
      evento.preventDefault();
      try { await api(cfg.caminho, { metodo: 'POST', corpo: lerFormulario(formulario, cfg.campos) }); avisar('Registro salvo'); mostrar(chave); } catch (erro) { avisar(erro.message, true); }
    });
    blocos.push(h('div', { classe: 'bloco' }, h('h2', { texto: 'Novo registro' }), formulario));
  }
  return h('div', { classe: 'grade' }, ...blocos);
}

// ---------------------------------------------------------------- painel
async function telaPainel() {
  const p = await api('/api/painel');
  const cartoes = [['Órgãos', p.orgaos], ['Contratos ativos', p.contratos], ['Projetos ativos', p.projetos], ['Profissionais', p.profissionais], ['Tarefas abertas', p.tarefas_abertas]];
  return h('div', {},
    h('div', { classe: 'cartoes' }, cartoes.map(([r, v]) => h('div', { classe: 'cartao' }, h('div', { classe: 'num', texto: numero(v) }), h('div', { classe: 'rot', texto: r })))),
    h('div', { classe: 'bloco' }, h('h2', { texto: 'Medição por contrato' }), tabela([
      ['Contrato', (c) => c.contrato.numero], ['Unidade', (c) => c.unidade], ['Contratado', (c) => numero(c.contratado)], ['Executado', (c) => numero(c.executado)],
      ['Aceito', (c) => numero(c.aceito)], ['Pago', (c) => numero(c.pago)], ['Saldo', (c) => numero(c.saldo)], ['Valor executado', (c) => reais(c.valor_executado)], ['Valor aceito', (c) => reais(c.valor_aceito)],
    ], p.contratos_resumo)),
    h('div', { classe: 'bloco' }, h('h2', { texto: 'Últimos START' }), tabela([
      ['Quando', (e) => new Date(e.em).toLocaleString('pt-BR')], ['Projeto', (e) => `#${e.projeto_id}`], ['Resultado', (e) => h('span', { classe: 'etq ' + e.resultado, texto: rotuloResultado(e.resultado) })],
    ], p.ultimos_start)));
}

const rotuloResultado = (r) => ({ INICIADO: 'Iniciado', INICIADO_SEM_AGENTES: 'Iniciado · agentes: integração pendente', BLOQUEADO: 'Bloqueado' }[r] || r);

// ---------------------------------------------------------------- projetos
async function telaProjetos() {
  await Promise.all(['/api/contratos', '/api/ordens-servico'].map(carregarLista));
  const projetos = await carregarLista('/api/projetos');
  const cartoes = await Promise.all(projetos.map(async (p) => {
    const sit = await api(`/api/projetos/${p.id}/situacao`).catch((e) => ({ erro: e.message }));
    const resultado = h('ul', { classe: 'etapas' });
    const linha = (rotulo, s) => h('li', {}, h('span', { classe: 'etq ' + (s?.situacao || 'PENDENTE'), texto: s?.situacao || '—' }), ` ${rotulo}: ${s?.mensagem || ''}`);
    return h('div', { classe: 'bloco' },
      h('h2', { texto: `${p.nome} (${p.codigo})` }),
      h('p', { classe: 'nota', texto: `Contrato ${nomePorId('/api/contratos', p.contrato_id, 'numero')} · OS ${nomePorId('/api/ordens-servico', p.os_id, 'numero')}` }),
      sit.erro ? h('p', { classe: 'erro', texto: sit.erro }) : h('ul', { classe: 'etapas' },
        linha('Banco de dados', sit.banco), linha('Serviço', sit.servico), linha('Código', sit.codigo),
        h('li', {}, h('span', { classe: 'etq ' + (sit.testes && !sit.testes.falhas && !sit.testes.erros ? 'OK' : 'PENDENTE'), texto: sit.testes ? `${sit.testes.total - sit.testes.falhas - sit.testes.erros}/${sit.testes.total}` : '—' }), ' Testes'),
        h('li', {}, h('span', { classe: 'etq PENDENTE', texto: 'Agentes' }), ` ${sit.agentes}`)),
      h('div', { classe: 'linha-botoes' },
        podeEscrever() ? h('button', { type: 'button', texto: 'START', onclick: () => acionarStart(p, resultado) }) : null,
        p.repositorio_url ? h('a', { href: p.repositorio_url, target: '_blank', rel: 'noopener', texto: 'Abrir repositório' }) : null,
        p.url_servico ? h('a', { href: p.url_servico, target: '_blank', rel: 'noopener', texto: 'Abrir sistema' }) : null),
      resultado);
  }));
  const blocos = [h('div', { classe: 'projetos' }, cartoes.length ? cartoes : h('p', { classe: 'nota', texto: 'Nenhum projeto cadastrado.' }))];
  if (podeEscrever()) {
    const campos = [['codigo', 'Código (letras minúsculas e hífen)', 'text', null, true], ['nome', 'Nome', 'text', null, true], ['contrato_id', 'Contrato', 'ref', '/api/contratos', false, 'numero'], ['os_id', 'Ordem de serviço', 'ref', '/api/ordens-servico', false, 'numero'], ['pasta', 'Pasta (relativa à pasta de projetos)'], ['repositorio_url', 'Endereço do repositório'], ['url_servico', 'Endereço do serviço (http://...)'], ['variavel_banco', 'Variável do banco (ex.: PROJ_X_DATABASE_URL)'], ['variavel_token', 'Variável do token (ex.: PROJ_X_TOKEN)']];
    const formulario = h('form', {}, campos.map(campoFormulario), h('button', { type: 'submit', texto: 'Cadastrar projeto' }));
    formulario.addEventListener('submit', async (evento) => {
      evento.preventDefault();
      try { await api('/api/projetos', { metodo: 'POST', corpo: lerFormulario(formulario, campos) }); avisar('Projeto cadastrado'); mostrar('projetos'); } catch (erro) { avisar(erro.message, true); }
    });
    blocos.push(h('div', { classe: 'bloco' }, h('h2', { texto: 'Cadastrar projeto existente' }), h('p', { classe: 'nota', texto: 'A senha do banco nunca é digitada aqui: informe só o nome da variável de ambiente que guarda a conexão.' }), formulario));
  }
  return h('div', {}, ...blocos);
}

async function acionarStart(projeto, destino) {
  destino.replaceChildren(h('li', { texto: 'Verificando…' }));
  try {
    const r = await api(`/api/projetos/${projeto.id}/start`, { metodo: 'POST' });
    destino.replaceChildren(h('li', {}, h('strong', { texto: 'Resultado: ' }), h('span', { classe: 'etq ' + r.resultado, texto: rotuloResultado(r.resultado) })),
      ...r.etapas.map((e) => h('li', {}, h('span', { classe: 'etq ' + e.situacao, texto: e.situacao }), ` ${e.etapa}: ${e.mensagem}`)));
  } catch (erro) { destino.replaceChildren(h('li', { classe: 'erro', texto: erro.message })); }
}

// ---------------------------------------------------------------- contratos: documentos e medição
async function telaContrato() {
  const contratos = await carregarLista('/api/contratos');
  const seletor = h('select', { id: 'contratoEscolhido' }, contratos.map((c) => h('option', { value: c.id, texto: `${c.numero} · ${c.objeto.slice(0, 60)}` })));
  const area = h('div', {});
  const desenhar = async () => {
    const id = Number(seletor.value);
    if (!id) return area.replaceChildren(h('p', { classe: 'nota', texto: 'Cadastre um contrato primeiro.' }));
    const [m, docs] = await Promise.all([api(`/api/contratos/${id}/medicao`), api(`/api/documentos?contrato_id=${id}`)]);
    const envio = h('form', {}, h('label', {}, 'Tipo', h('select', { name: 'tipo' }, ['EDITAL', 'TR', 'CONTRATO', 'OS', 'TERMO_ACEITE', 'OUTRO'].map((t) => h('option', { value: t, texto: t })))),
      h('label', {}, 'Título', h('input', { name: 'titulo', required: true, minlength: 3 })), h('label', {}, 'Arquivo', h('input', { name: 'arquivo', type: 'file', required: true })),
      h('button', { type: 'submit', texto: 'Anexar' }));
    envio.addEventListener('submit', async (evento) => {
      evento.preventDefault();
      const dados = new FormData(envio); dados.append('contrato_id', String(id));
      try { await api('/api/documentos', { metodo: 'POST', formulario: dados }); avisar('Documento anexado'); desenhar(); } catch (erro) { avisar(erro.message, true); }
    });
    area.replaceChildren(
      h('div', { classe: 'cartoes' }, [['Contratado', m.contratado], ['Executado', m.executado], ['Aceito', m.aceito], ['Pago', m.pago], ['Saldo', m.saldo]].map(([r, v]) => h('div', { classe: 'cartao' }, h('div', { classe: 'num', texto: numero(v) }), h('div', { classe: 'rot', texto: `${r} (${m.unidade})` }))),
        h('div', { classe: 'cartao' }, h('div', { classe: 'num', texto: reais(m.valor_executado) }), h('div', { classe: 'rot', texto: 'Valor executado' }))),
      h('div', { classe: 'bloco' }, h('h2', { texto: 'Relatório de medição' }), h('div', { classe: 'linha-botoes' }, ['docx', 'pdf', 'xlsx'].map((f) => h('button', { classe: 'secundario', type: 'button', texto: { docx: 'Word', pdf: 'PDF', xlsx: 'Excel' }[f], onclick: () => baixar(`/api/relatorios/medicao/${id}.${f}`, `medicao.${f}`) })))),
      h('div', { classe: 'bloco' }, h('h2', { texto: 'Itens medidos' }), tabela([['Data', (i) => dataBr(i.data_execucao)], ['Item', (i) => i.item], ['Descrição', (i) => i.descricao], ['Quantidade', (i) => numero(i.quantidade)], ['Situação', (i) => h('span', { classe: 'etq', texto: i.situacao })], ['Aceite', (i) => i.documento_aceite]], m.itens)),
      h('div', { classe: 'grade' },
        h('div', { classe: 'bloco' }, h('h2', { texto: 'Edital, TR, contrato e OS anexados' }), tabela([['Tipo', (d) => d.tipo], ['Título', (d) => d.titulo], ['Arquivo', (d) => h('button', { classe: 'secundario', type: 'button', texto: d.nome_arquivo, onclick: () => baixar(`/api/documentos/${d.id}/arquivo`, d.nome_arquivo) })], ['Enviado em', (d) => dataBr(d.enviado_em)]], docs)),
        podeEscrever() ? h('div', { classe: 'bloco' }, h('h2', { texto: 'Anexar documento' }), envio) : null));
  };
  seletor.addEventListener('change', desenhar);
  await desenhar();
  return h('div', {}, h('label', {}, 'Contrato', seletor), area);
}

// ---------------------------------------------------------------- horas
async function telaHoras() {
  await Promise.all(['/api/profissionais', '/api/agentes', '/api/projetos', '/api/contratos'].map(carregarLista));
  const mesAtual = new Date().toISOString().slice(0, 7);
  const filtro = h('input', { type: 'month', id: 'mesHoras', value: estado.mesHoras || mesAtual });
  const area = h('div', {});
  const desenhar = async () => {
    estado.mesHoras = filtro.value;
    const [lancs, resumo] = await Promise.all([api(`/api/horas?mes=${filtro.value}`), api(`/api/horas/resumo?mes=${filtro.value}`)]);
    const quem = (r) => (r.tipo === 'profissional' ? nomePorId('/api/profissionais', r.id) : nomePorId('/api/agentes', r.id, 'codigo') + ' (IA)');
    area.replaceChildren(
      h('div', { classe: 'cartoes' }, [['Horas humanas registradas', resumo.total.humanas], ['Horas humanas aceitas', resumo.total.aceitas], ['Horas de IA', resumo.total.ia]].map(([r, v]) => h('div', { classe: 'cartao' }, h('div', { classe: 'num', texto: numero(v) }), h('div', { classe: 'rot', texto: r })))),
      h('div', { classe: 'bloco' }, h('h2', { texto: 'Relatório do mês' }), h('div', { classe: 'linha-botoes' }, ['docx', 'pdf', 'xlsx'].map((f) => h('button', { classe: 'secundario', type: 'button', texto: { docx: 'Word', pdf: 'PDF', xlsx: 'Excel' }[f], onclick: () => baixar(`/api/relatorios/horas.${f}?mes=${filtro.value}`, `horas_${filtro.value}.${f}`) })))),
      h('div', { classe: 'bloco' }, h('h2', { texto: `Inconsistências para conferir (${resumo.inconsistencias.length})` }),
        resumo.inconsistencias.length ? h('ul', { classe: 'etapas' }, resumo.inconsistencias.map((a) => h('li', {}, h('span', { classe: 'etq PENDENTE', texto: a.tipo }), ` ${a.mensagem} (lançamentos ${a.lancamentos.join(', ')})`))) : h('p', { classe: 'nota', texto: 'Nenhuma inconsistência. O sistema só aponta: ele não altera seus lançamentos.' })),
      h('div', { classe: 'bloco' }, h('h2', { texto: 'Totais por pessoa e agente no mês' }), tabela([['Quem', quem], ['Humanas', (r) => numero(r.humanas)], ['Aceitas', (r) => numero(r.aceitas)], ['IA', (r) => numero(r.ia)]], resumo.por_mes)),
      h('div', { classe: 'bloco' }, h('h2', { texto: 'Totais por dia' }), tabela([['Data', (r) => dataBr(r.data)], ['Quem', quem], ['Humanas', (r) => numero(r.humanas)], ['Aceitas', (r) => numero(r.aceitas)], ['IA', (r) => numero(r.ia)]], resumo.por_dia)),
      h('div', { classe: 'bloco' }, h('h2', { texto: `Lançamentos (${lancs.length})` }), tabela([
        ['Nº', (l) => l.id], ['Data', (l) => dataBr(l.data)], ['Tipo', (l) => l.tipo], ['Quem', (l) => (l.tipo === 'HUMANA' ? nomePorId('/api/profissionais', l.profissional_id) : nomePorId('/api/agentes', l.agente_id, 'codigo'))],
        ['Período', (l) => `${l.inicio.slice(0, 5)}–${l.fim.slice(0, 5)} (−${l.intervalo_min} min)`], ['Horas', (l) => numero(l.horas)], ['Atividade', (l) => l.atividade],
        ['Faturamento', (l) => (l.aceita ? h('span', { classe: 'etq OK', texto: 'Aceita' }) : l.tipo === 'HUMANA' && podeEscrever() ? h('button', { classe: 'secundario', type: 'button', texto: 'Registrar aceite', onclick: () => registrarAceite(l.id, desenhar) }) : '—')],
      ], lancs)));
  };
  filtro.addEventListener('change', desenhar);
  const blocos = [h('div', { classe: 'bloco' }, h('label', {}, 'Mês', filtro)), area];
  if (podeEscrever()) blocos.push(formularioHoras(desenhar));
  await desenhar();
  return h('div', {}, ...blocos);
}

function formularioHoras(aoSalvar) {
  const campos = [['tipo', 'Tipo', 'select', 'tipo_hora', true], ['profissional_id', 'Profissional (hora humana)', 'ref', '/api/profissionais'], ['agente_id', 'Agente (hora de IA)', 'ref', '/api/agentes', false, 'codigo'], ['projeto_id', 'Projeto', 'ref', '/api/projetos', false, 'codigo'], ['contrato_id', 'Contrato', 'ref', '/api/contratos', false, 'numero'], ['data', 'Data', 'date', null, true], ['inicio', 'Início', 'time', null, true], ['fim', 'Fim', 'time', null, true], ['intervalo_min', 'Intervalo (minutos)', 'number'], ['atividade', 'Atividade realizada', 'textarea', null, true], ['evidencia', 'Evidência (commit, ata, link)']];
  OPCOES.tipo_hora = ['HUMANA', 'IA'];
  const formulario = h('form', {}, campos.map(campoFormulario), h('button', { type: 'submit', texto: 'Lançar horas' }));
  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    try { await api('/api/horas', { metodo: 'POST', corpo: lerFormulario(formulario, campos) }); avisar('Horas lançadas'); formulario.reset(); aoSalvar(); } catch (erro) { avisar(erro.message, true); }
  });
  return h('div', { classe: 'bloco' }, h('h2', { texto: 'Lançar horas trabalhadas' }), h('p', { classe: 'nota', texto: 'Preenchimento manual. Hora humana exige o profissional; hora de IA exige o agente e nunca entra em nome de pessoa.' }), formulario);
}

function registrarAceite(id, aoSalvar) {
  const dialogo = h('form', { classe: 'bloco' }, h('h2', { texto: `Aceite do lançamento ${id}` }),
    h('label', {}, 'Aceito por (nome e cargo no órgão)', h('input', { name: 'aceito_por', required: true, minlength: 3 })),
    h('label', {}, 'Documento (termo, ofício, e-mail)', h('input', { name: 'documento', required: true, minlength: 3 })),
    h('label', {}, 'Data', h('input', { name: 'aceito_em', type: 'date', required: true })),
    h('div', { classe: 'linha-botoes' }, h('button', { type: 'submit', texto: 'Registrar' }), h('button', { classe: 'secundario', type: 'button', texto: 'Cancelar', onclick: () => dialogo.remove() })));
  dialogo.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    try { await api(`/api/horas/${id}/aceite`, { metodo: 'POST', corpo: Object.fromEntries(new FormData(dialogo)) }); avisar('Aceite registrado'); dialogo.remove(); aoSalvar(); } catch (erro) { avisar(erro.message, true); }
  });
  el('conteudo').prepend(dialogo);
  dialogo.querySelector('input').focus();
}

// ---------------------------------------------------------------- testes dos projetos
async function telaTestes() {
  const projetos = await carregarLista('/api/projetos');
  const seletor = h('select', {}, projetos.map((p) => h('option', { value: p.id, texto: p.codigo })));
  const area = h('div', {});
  const desenhar = async () => {
    if (!seletor.value) return area.replaceChildren(h('p', { classe: 'nota', texto: 'Cadastre um projeto primeiro.' }));
    const execucoes = await api(`/api/projetos/${seletor.value}/testes`);
    area.replaceChildren(tabela([['Quando', (e) => new Date(e.executado_em).toLocaleString('pt-BR')], ['Origem', (e) => e.origem], ['Total', (e) => e.total], ['Falhas', (e) => e.falhas], ['Erros', (e) => e.erros], ['Ignorados', (e) => e.ignorados]], execucoes));
  };
  const envio = h('form', {}, h('label', {}, 'Resultado JUnit (XML gerado pelo pytest, Jest, Maven…)', h('input', { name: 'arquivo', type: 'file', accept: '.xml', required: true })), h('button', { type: 'submit', texto: 'Importar resultado' }));
  envio.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    try { await api(`/api/projetos/${seletor.value}/testes`, { metodo: 'POST', formulario: new FormData(envio) }); avisar('Resultado importado'); desenhar(); } catch (erro) { avisar(erro.message, true); }
  });
  seletor.addEventListener('change', desenhar);
  await desenhar();
  return h('div', { classe: 'grade' }, h('div', { classe: 'bloco' }, h('label', {}, 'Projeto', seletor), area), podeEscrever() ? h('div', { classe: 'bloco' }, h('h2', { texto: 'Importar testes executados' }), envio) : null);
}

// ---------------------------------------------------------------- usuários
async function telaUsuarios() {
  const usuarios = await api('/api/usuarios');
  OPCOES.perfil = ['GESTOR', 'CONSULTA', 'ADMIN'];
  const campos = [['nome', 'Nome', 'text', null, true], ['login', 'Login', 'text', null, true], ['senha', 'Senha (12+ caracteres)', 'password', null, true], ['perfil', 'Perfil', 'select', 'perfil', true]];
  const formulario = h('form', {}, campos.map(campoFormulario), h('button', { type: 'submit', texto: 'Criar usuário' }));
  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    try { await api('/api/usuarios', { metodo: 'POST', corpo: lerFormulario(formulario, campos) }); avisar('Usuário criado'); mostrar('usuarios'); } catch (erro) { avisar(erro.message, true); }
  });
  return h('div', { classe: 'grade' }, h('div', { classe: 'bloco' }, tabela([['Nome', (u) => u.nome], ['Login', (u) => u.login], ['Perfil', (u) => u.perfil], ['Ativo', (u) => (u.ativo ? 'Sim' : 'Não')]], usuarios)), h('div', { classe: 'bloco' }, h('h2', { texto: 'Novo usuário' }), formulario));
}

// ---------------------------------------------------------------- navegação
const TELAS = [
  ['painel', 'Painel', telaPainel], ['projetos', 'Projetos e START', telaProjetos], ['contrato', 'Contrato: medição e documentos', telaContrato],
  ['horas', 'Horas', telaHoras], ['orgaos', 'Órgãos'], ['contratos', 'Contratos'], ['ordens-servico', 'Ordens de serviço'], ['profissionais', 'Profissionais'],
  ['agentes', 'Agentes'], ['tarefas', 'Tarefas'], ['evidencias', 'Evidências'], ['testes', 'Testes', telaTestes], ['medicoes', 'Medições'], ['usuarios', 'Usuários', telaUsuarios],
];

async function mostrar(tela) {
  estado.tela = tela;
  const [, titulo, funcao] = TELAS.find(([chave]) => chave === tela);
  el('titulo').textContent = titulo;
  document.querySelectorAll('#menu button').forEach((b) => b.classList.toggle('ativo', b.dataset.tela === tela));
  el('conteudo').replaceChildren(h('p', { classe: 'nota', texto: 'Carregando…' }));
  try { el('conteudo').replaceChildren(await (funcao ? funcao() : telaCadastro(tela))); } catch (erro) { el('conteudo').replaceChildren(h('p', { classe: 'erro', texto: erro.message })); }
}

function montarMenu() {
  el('menu').replaceChildren(...TELAS.filter(([chave]) => chave !== 'usuarios' || estado.usuario.perfil === 'ADMIN')
    .map(([chave, titulo]) => h('button', { type: 'button', 'data-tela': chave, texto: titulo, onclick: () => mostrar(chave) })));
}

async function iniciar() {
  if (!estado.token) { el('telaLogin').hidden = false; el('app').hidden = true; return; }
  try { estado.usuario = await api('/api/eu'); } catch { return; }
  el('telaLogin').hidden = true; el('app').hidden = false;
  el('quem').textContent = `${estado.usuario.nome} · ${estado.usuario.perfil}`;
  montarMenu();
  mostrar(estado.tela);
}

async function sair(avisarServidor = true) {
  if (avisarServidor) await api('/api/logout', { metodo: 'POST' }).catch(() => {});
  guardarToken(null); estado.token = null; estado.usuario = null;
  el('app').hidden = true; el('telaLogin').hidden = false;
}

el('formLogin').addEventListener('submit', async (evento) => {
  evento.preventDefault();
  el('erroLogin').textContent = '';
  try {
    const r = await api('/api/login', { metodo: 'POST', corpo: { login: el('login').value, senha: el('senha').value } });
    estado.token = r.token; guardarToken(r.token); el('senha').value = '';
    iniciar();
  } catch (erro) { el('erroLogin').textContent = erro.message; }
});
el('sair').addEventListener('click', () => sair());
iniciar();
