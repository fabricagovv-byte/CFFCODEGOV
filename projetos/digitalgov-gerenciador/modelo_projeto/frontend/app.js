'use strict';

const el = (id) => document.getElementById(id);

async function carregar() {
  const saude = await fetch('/health').then((r) => r.json()).catch(() => null);
  el('situacao').textContent = saude ? `banco ok, migração ${saude.migracao}` : 'sem conexão com a API';
  const registros = await fetch('/api/registros').then((r) => r.json()).catch(() => []);
  el('lista').replaceChildren(...registros.map((r) => {
    const item = document.createElement('li');
    item.textContent = `#${r.id} · ${r.titulo}`;
    return item;
  }));
}

el('novo').addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const resposta = await fetch('/api/registros', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ titulo: el('titulo').value, descricao: el('descricao').value || null }),
  });
  el('aviso').textContent = resposta.ok ? 'Registro gravado no banco.' : 'Não foi possível gravar.';
  if (resposta.ok) evento.target.reset();
  carregar();
});

carregar();
