const { chromium } = require('playwright');
const [BASE, OUT] = process.argv.slice(2);
const log = (ok, msg) => console.log(`${ok ? 'PASS' : 'FAIL'}  ${msg}`);
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto(BASE);
  await page.waitForSelector('#connection[data-state="ok"]');
  log(true, 'E01 painel carrega e indica "Conectado"');
  await page.click('#create-btn');
  log(await page.isVisible('#name-error'), 'E02 nome vazio exibe erro no formulário');
  const add = async (name, pref) => {
    await page.fill('#name', name);
    await page.check(`input[value="${pref ? 'preferencial' : 'normal'}"]`, { force: true });
    await page.click('#create-btn');
    await page.waitForFunction(n => [...document.querySelectorAll('#queue-list .ticket-name')].some(e => e.textContent === n), name);
  };
  await add('Ana Souza'); await add('Bruno Lima', true); await add('<img src=x onerror=alert(1)>'); await add('Carla Dias', true);
  const order = await page.$$eval('#queue-list .ticket-code', e => e.map(x => x.textContent).join(' '));
  log(order === 'P-002 P-004 N-001 N-003', `E03 fila em ordem de chamada: ${order}`);
  log(await page.$$eval('#queue-list img', e => e.length) === 0, 'E04 nome com HTML exibido como texto (sem <img> criado)');
  log((await page.textContent('#next-preview .ticket-code')) === 'P-002', 'E05 "Próximo da fila" mostra P-002');
  await page.screenshot({ path: OUT + '/painel-desktop.png', fullPage: true });
  await page.click('#call-btn'); await page.waitForSelector('#called-list li');
  await page.click('#call-btn'); await page.waitForFunction(() => document.querySelectorAll('#called-list li').length === 2);
  const called = await page.$$eval('#called-list .ticket-code', e => e.map(x => x.textContent).join(' '));
  log(called === 'P-002 P-004', `E06 chamar próximo duas vezes: ${called}`);
  await page.click('#called-list li:first-child button'); await page.waitForSelector('#done-list li');
  const stats = await page.$$eval('.stat-value', e => e.map(x => x.textContent).join('/'));
  log(stats === '2/0/1/1', `E07 concluir atualiza indicadores (aguardando/pref/atendimento/concluídos): ${stats}`);
  // Ação feita fora do painel (outro terminal) deve aparecer pela atualização automática
  await fetch(BASE + 'tickets', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: 'Outro terminal' }) });
  await page.waitForFunction(() => [...document.querySelectorAll('#queue-list .ticket-name')].some(e => e.textContent === 'Outro terminal'), null, { timeout: 8000 });
  log(true, 'E08 senha criada por outro cliente aparece em até 8 s (polling de 5 s)');
  for (let i = 0; i < 3; i++) { await page.click('#call-btn'); await page.waitForTimeout(250); }
  log(await page.isDisabled('#call-btn'), 'E09 com fila vazia, "Chamar próximo" fica desabilitado');
  // Somente teclado
  await page.focus('#name'); await page.keyboard.type('Teclado Silva'); await page.keyboard.press('Enter');
  await page.waitForFunction(() => [...document.querySelectorAll('#queue-list .ticket-name')].some(e => e.textContent === 'Teclado Silva'));
  log(true, 'E10 cadastro apenas com teclado (Enter envia o formulário)');
  const m = await browser.newPage({ viewport: { width: 375, height: 800 }, colorScheme: 'dark' });
  await m.goto(BASE); await m.waitForSelector('#connection[data-state="ok"]');
  log(!(await m.evaluate(() => document.documentElement.scrollWidth > innerWidth)), 'E11 375 px em modo escuro sem rolagem horizontal');
  await m.screenshot({ path: OUT + '/painel-celular-escuro.png', fullPage: true });
  log(errors.length === 0, `E12 nenhum erro no console${errors.length ? ': ' + errors.join(' | ') : ''}`);
  await browser.close();
})().catch(e => { console.log('FAIL  execução interrompida: ' + e.message); process.exit(1); });
