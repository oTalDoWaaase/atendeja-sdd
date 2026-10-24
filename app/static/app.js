// Painel AtendeJá: consome somente a API REST pública (mesma origem), sem dependências.
'use strict';

const REFRESH_MS = 5000;
const DONE_LIMIT = 20;
const NAME_MAX = 80;

const $ = (id) => document.getElementById(id);
const els = {
  form: $('ticket-form'), name: $('name'), nameCount: $('name-count'), nameError: $('name-error'),
  createBtn: $('create-btn'), callBtn: $('call-btn'), nextPreview: $('next-preview'),
  calledList: $('called-list'), calledEmpty: $('called-empty'),
  queueList: $('queue-list'), queueEmpty: $('queue-empty'),
  doneList: $('done-list'), doneEmpty: $('done-empty'),
  connection: $('connection'), toast: $('toast'),
  stats: { waiting: $('stat-waiting'), preferred: $('stat-preferred'), called: $('stat-called'), done: $('stat-done') },
};

let refreshSeq = 0;
let toastTimer = null;

// ---------- API ----------

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    ...options,
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(errorMessage(body, response.status));
    error.status = response.status;
    throw error;
  }
  return body;
}

// A API devolve `detail` como texto (regras de domínio) ou lista (validação do FastAPI).
function errorMessage(body, status) {
  const detail = body && body.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail.length) {
    const first = detail[0];
    if (first.loc && first.loc.includes('name')) return `Nome deve conter entre 1 e ${NAME_MAX} caracteres.`;
    return first.msg || 'Dados inválidos.';
  }
  return `Erro inesperado (HTTP ${status}).`;
}

// ---------- Renderização (somente textContent: nomes nunca são interpretados como HTML) ----------

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function ticketCode(ticket) {
  return `${ticket.priority === 'preferencial' ? 'P' : 'N'}-${String(ticket.id).padStart(3, '0')}`;
}

function badge(priority) {
  return el('span', `badge badge-${priority}`, priority === 'preferencial' ? 'Preferencial' : 'Normal');
}

function timeOf(iso) {
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? '' : date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function renderQueue(queue) {
  els.queueList.replaceChildren(...queue.map((ticket, index) => {
    const li = el('li', ticket.priority === 'preferencial' ? 'is-preferencial' : '');
    li.append(
      el('span', 'position', String(index + 1)),
      el('span', 'ticket-code', ticketCode(ticket)),
      el('span', 'ticket-name', ticket.name),
      badge(ticket.priority),
    );
    li.title = `Chegada às ${timeOf(ticket.created_at)}`;
    return li;
  }));
  els.queueEmpty.hidden = queue.length > 0;

  const next = queue[0];
  if (next) {
    const wrapper = el('div');
    const row = el('div', 'row');
    row.append(el('span', 'ticket-code', ticketCode(next)), document.createTextNode(' '), badge(next.priority));
    wrapper.append(row, el('div', 'ticket-name', next.name));
    els.nextPreview.replaceChildren(wrapper);
  } else {
    els.nextPreview.replaceChildren(el('p', 'empty', 'Nenhuma senha aguardando.'));
  }
  els.callBtn.disabled = !next;
}

function renderCalled(called) {
  els.calledList.replaceChildren(...called.map((ticket) => {
    const li = el('li');
    const row = el('div', 'row');
    row.append(el('span', 'ticket-code', ticketCode(ticket)), badge(ticket.priority));
    const button = el('button', 'btn btn-primary btn-sm', 'Concluir atendimento');
    button.type = 'button';
    button.addEventListener('click', () => finishTicket(ticket, button));
    li.append(row, el('span', 'ticket-name', ticket.name), el('span', 'meta', `Chegada às ${timeOf(ticket.created_at)}`), button);
    return li;
  }));
  els.calledEmpty.hidden = called.length > 0;
}

function renderDone(done) {
  const recent = done.slice(-DONE_LIMIT).reverse();
  els.doneList.replaceChildren(...recent.map((ticket) => {
    const li = el('li');
    li.append(el('span', 'ticket-code', ticketCode(ticket)), el('span', 'ticket-name', ticket.name), badge(ticket.priority));
    return li;
  }));
  els.doneEmpty.hidden = done.length > 0;
}

function render(tickets, queue) {
  const called = tickets.filter((t) => t.status === 'chamado');
  const done = tickets.filter((t) => t.status === 'concluido');
  els.stats.waiting.textContent = queue.length;
  els.stats.preferred.textContent = queue.filter((t) => t.priority === 'preferencial').length;
  els.stats.called.textContent = called.length;
  els.stats.done.textContent = done.length;
  renderQueue(queue);
  renderCalled(called);
  renderDone(done);
}

function setConnection(ok) {
  els.connection.dataset.state = ok ? 'ok' : 'error';
  els.connection.textContent = ok ? 'Conectado' : 'Sem conexão com a API';
}

function toast(message, kind = 'info') {
  els.toast.textContent = message;
  els.toast.dataset.kind = kind;
  els.toast.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { els.toast.hidden = true; }, 4000);
}

// ---------- Ações ----------

async function refresh() {
  const seq = ++refreshSeq;
  try {
    const [tickets, queue] = await Promise.all([api('/tickets'), api('/queue')]);
    if (seq !== refreshSeq) return; // resposta antiga: uma atualização mais nova já foi disparada
    render(tickets, queue);
    setConnection(true);
  } catch (error) {
    if (seq === refreshSeq) setConnection(false);
  }
}

function validateName() {
  const value = els.name.value.trim();
  const message = value.length === 0 || value.length > NAME_MAX ? `Nome deve conter entre 1 e ${NAME_MAX} caracteres.` : '';
  showNameError(message);
  return message === '';
}

function showNameError(message) {
  els.nameError.textContent = message;
  els.nameError.hidden = !message;
  els.name.setAttribute('aria-invalid', message ? 'true' : 'false');
}

async function createTicket(event) {
  event.preventDefault();
  if (!validateName()) { els.name.focus(); return; }
  const priority = els.form.elements.priority.value;
  els.createBtn.disabled = true;
  try {
    const ticket = await api('/tickets', { method: 'POST', body: JSON.stringify({ name: els.name.value, priority }) });
    toast(`Senha ${ticketCode(ticket)} gerada para ${ticket.name}.`);
    els.form.reset();
    els.nameCount.textContent = '0';
    els.name.focus();
  } catch (error) {
    if (error.status === 422) showNameError(error.message);
    else toast(error.message, 'error');
  } finally {
    els.createBtn.disabled = false;
    refresh();
  }
}

async function callNext() {
  els.callBtn.disabled = true;
  try {
    const ticket = await api('/tickets/next', { method: 'POST' });
    toast(`Chamando ${ticketCode(ticket)} — ${ticket.name}`);
  } catch (error) {
    toast(error.message, 'error');
  } finally {
    refresh();
  }
}

async function finishTicket(ticket, button) {
  button.disabled = true;
  try {
    await api(`/tickets/${ticket.id}/finish`, { method: 'POST' });
    toast(`Atendimento ${ticketCode(ticket)} concluído.`);
  } catch (error) {
    toast(error.message, 'error');
  } finally {
    refresh();
  }
}

// ---------- Inicialização ----------

els.form.addEventListener('submit', createTicket);
els.callBtn.addEventListener('click', callNext);
els.name.addEventListener('input', () => {
  els.nameCount.textContent = String(els.name.value.length);
  if (!els.nameError.hidden) validateName();
});

// Atualização periódica para refletir ações de outros terminais; pausa com a aba oculta.
setInterval(() => { if (!document.hidden) refresh(); }, REFRESH_MS);
document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });
refresh();
