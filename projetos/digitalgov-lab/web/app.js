'use strict';
const $=id=>document.getElementById(id);
const fmt=n=>new Intl.NumberFormat('pt-BR').format(n ?? 0);
const cell=(row,value)=>{const td=document.createElement('td');td.textContent=value==null?'—':String(value);row.appendChild(td);return td};
const status=(row,value)=>{const td=document.createElement('td');const sp=document.createElement('span');sp.className='pill';sp.textContent=value;td.appendChild(sp);row.appendChild(td)};
const date=x=>x?new Date(x).toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo'}):'—';
const duration=x=>{if(!x)return '0h 00m';const seconds=Number(x);return `${Math.floor(seconds/3600)}h ${String(Math.floor((seconds%3600)/60)).padStart(2,'0')}m`};
let rows=[];
function draw(d){
 $('m_target').textContent=fmt(d.target_ust);$('m_verified').textContent=fmt(d.internal_verified_ust);$('m_accepted').textContent=fmt(d.official_accepted_ust);
 $('m_agents').textContent=fmt(d.active_agent_processes);$('m_projects').textContent=fmt(d.project_count);$('m_audit').textContent=d.audit_chain_valid?'ÍNTEGRA':'FALHA';
 $('m_open').textContent=fmt(d.tasks.filter(t=>t.state==='ABERTA').length);$('m_running').textContent=fmt(d.tasks.filter(t=>t.state==='EM_EXECUCAO').length);
 const percentage=d.target_ust?100*d.internal_verified_ust/d.target_ust:0;$('percentage').textContent=percentage.toLocaleString('pt-BR',{maximumFractionDigits:2})+'%';$('bar').style.width=Math.min(100,percentage)+'%';
 $('updated').textContent='Atualizado em '+date(d.fetched_at);
 $('warnings').textContent=d.catalog_status+'. Nenhuma meta das 15 OS simuladas pode ser faturada. UST faturáveis: '+fmt(d.billable_ust)+'.';
 rows=d.orders;renderOrders();
 const team=$('teamrows');team.replaceChildren();d.team.forEach(p=>{const tr=document.createElement('tr');cell(tr,p.name??'Vaga pendente');cell(tr,p.role);cell(tr,p.shift_start+'–'+p.shift_end);cell(tr,fmt(p.ust_meta_supervisionadas));cell(tr,duration(p.human_seconds_recorded));team.appendChild(tr)});
 const tasks=$('tasks');tasks.replaceChildren();d.tasks.forEach(t=>{const tr=document.createElement('tr');cell(tr,'#'+t.id+' '+t.description);cell(tr,t.order_id);cell(tr,t.assignee_kind+' · '+t.assignee);cell(tr,date(t.started_at));cell(tr,date(t.finished_at));status(tr,t.state);cell(tr,t.test_result);tasks.appendChild(tr)});$('emptyTasks').hidden=d.tasks.length>0;
}
function renderOrders(){const filter=$('filter').value.toLocaleLowerCase('pt-BR'),tbody=$('orders');tbody.replaceChildren();rows.filter(x=>(x.project_id+' '+x.macroservice+' '+x.id).toLocaleLowerCase('pt-BR').includes(filter)).forEach(x=>{const tr=document.createElement('tr');cell(tr,x.project_id+' / '+x.id);cell(tr,x.macroservice);cell(tr,x.overseer||'—');cell(tr,fmt(x.ust_target));cell(tr,fmt(x.ust_verified_lab));cell(tr,fmt(x.ust_official_accepted));status(tr,x.status);tbody.appendChild(tr)})}
$('filter').addEventListener('input',renderOrders);
async function load(){try{const r=await fetch('/api/state',{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);draw(await r.json())}catch(e){$('updated').textContent='Falha ao consultar o banco: '+e.message;document.querySelector('.live').textContent='Sem conexão'}}
load();setInterval(load,5000);

async function loadCatalog(){
 try{
  const r=await fetch('/api/catalog',{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);
  const catalog=(await r.json()).services;const parent=$('servicecards');parent.replaceChildren();
  catalog.forEach(s=>{
   const art=document.createElement('article');art.className='servicecard';
   const eyebrow=document.createElement('small');eyebrow.textContent=s.id+' · SERVIÇO '+String(s.code).padStart(2,'0');art.appendChild(eyebrow);
   const title=document.createElement('h3');title.textContent=s.name;art.appendChild(title);
   const desc=document.createElement('p');desc.textContent=s.description;art.appendChild(desc);
   const link=document.createElement('a');link.href='http://127.0.0.1:'+s.port+'/service';link.target='_blank';link.rel='noopener noreferrer';link.textContent='Abrir operação local';art.appendChild(link);parent.appendChild(art);
  });
 }catch(e){$('servicecards').textContent='Falha ao carregar catálogo: '+e.message}
}
loadCatalog();
