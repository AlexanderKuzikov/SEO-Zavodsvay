/* ============================================================================
 * Вебмастер-монитор zavodsvay.ru — приложение (vanilla, без зависимостей)
 * Данные: ../data/webmaster/data.json (генерирует scripts/webmaster_monitor.py)
 * Срезы: регион (11108 / all) × устройство (desktop / mobile)
 * Позиция считается по странице-приёмнику из ядра (core.csv).
 * ========================================================================== */

'use strict';

const DATA_URL = '../data/webmaster/data.json';
const SITE = 'https://zavodsvay.ru';
const REGION_NAMES = { '11108': 'Пермский край', 'all': 'Вся Россия' };
const DEVICE_NAMES = { 'desktop': 'Десктоп', 'mobile': 'Мобильные' };

const state = {
  region: '11108',
  device: 'desktop',
  search: '',
  type: '',
  priority: '',
  onlyFound: false,
  sortKey: 'pos',
  sortDir: 1,
};

let DATA = null;
let slice = null; // { queries: [{ entry, pages, targetPage, posToday, posPrev, delta, imp, clicks, ctr }] }

const $ = id => document.getElementById(id);

/* ─── Нормализация ──────────────────────────────────────────────────────── */
function normUrl(u) {
  return String(u || '').toLowerCase()
    .replace(/^https?:\/\//, '').replace(/^www\./, '').replace(/\/+$/, '');
}
function targetUrl(landing) {
  const path = landing && landing !== '/' ? landing.replace(/^\/?/, '/') : '/';
  return normUrl(SITE + path);
}
function fmtNum(n) {
  if (n == null || isNaN(n)) return '—';
  if (n >= 1000000) return (n / 1000000).toFixed(1).replace('.0', '') + ' млн';
  if (n >= 1000) return (n / 1000).toFixed(1).replace('.0', '') + ' тыс.';
  return String(n);
}
function fmtCtr(v) {
  if (v == null || isNaN(v)) return '—';
  return v.toFixed(1) + '%';
}
function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

/* ─── Загрузка данных ───────────────────────────────────────────────────── */
async function load() {
  try {
    const res = await fetch(DATA_URL, { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    DATA = await res.json();
    buildSlice();
  } catch (e) {
    $('statusChip').className = 'status-chip error';
    $('statusChip').textContent = 'данные не найдены';
    $('tbody').innerHTML = '<tr><td colspan="10"><div class="empty-state">' +
      '<div class="title">Файл данных не найден</div>' +
      'Запустите <code>python scripts/webmaster_monitor.py</code>, затем сервер:<br>' +
      '<code>python serve_ui.py</code></div></td></tr>';
    console.error(e);
  }
}

/* ─── Срез данных ───────────────────────────────────────────────────────── */
function buildSlice() {
  const reg = state.region, dev = state.device;
  const out = [];
  for (const q of (DATA.queries || [])) {
    const regs = q['регионы'] || {};
    const sliceData = (regs[reg] || {})[dev] || {};
    const pages = sliceData; // { url: { date: {position, impressions, clicks, ctr} } }
    const tKey = targetUrl(q['приёмник']);

    let page = pages[tKey];
    if (!page) page = {};
    const dates = Object.keys(page).sort();
    const latestWith = field => {
      for (let i = dates.length - 1; i >= 0; i--) {
        if (page[dates[i]][field] != null) return page[dates[i]][field];
      }
      return null;
    };
    const posToday = latestWith('position');

    // вчера: последняя дата с позицией, раньше самой свежей даты с позицией
    let posPrev = null;
    if (dates.length > 0) {
      const lastDate = dates[dates.length - 1];
      for (let i = dates.length - 2; i >= 0; i--) {
        if (page[dates[i]].position != null) { posPrev = page[dates[i]].position; break; }
      }
    }

    // показы/клики/CTR — сумма/среднее за окно
    let imp = 0, clicks = 0, ctrSum = 0, ctrN = 0;
    for (const d of dates) {
      const s = page[d];
      if (s.impressions != null) imp += s.impressions;
      if (s.clicks != null) clicks += s.clicks;
      if (s.ctr != null) { ctrSum += s.ctr; ctrN++; }
    }

    // серия позиций для спарклайна (только приёмник)
    const series = dates.map(d => ({ date: d, pos: page[d].position })).filter(p => p.pos != null);

    const otherPages = Object.keys(pages)
      .filter(u => u !== tKey)
      .map(u => ({ url: u, data: pages[u] }));

    out.push({
      q, pages, tKey, dates,
      page, posToday, posPrev,
      delta: posToday != null && posPrev != null ? posToday - posPrev : null,
      imp, clicks,
      ctr: ctrN ? ctrSum / ctrN : null,
      series, otherPages,
      inSerp: Object.keys(pages).length > 0,
      targetRanks: posToday != null,
      wrongPage: Object.keys(pages).length > 0 && posToday == null,
    });
  }
  slice = out;
  renderAll();
}

/* ─── Сортировка ────────────────────────────────────────────────────────── */
const SORT_GET = {
  text: r => r.q['text'].toLowerCase(),
  type: r => r.q['тип'],
  priority: r => ({ high: 0, med: 1, low: 2 }[r.q['приоритет']] ?? 9),
  freq: r => parseInt(r.q['частота'] || '0') || 0,
  pos: r => r.posToday,
  delta: r => r.delta,
  impressions: r => r.imp,
  clicks: r => r.clicks,
  ctr: r => r.ctr,
  spark: r => r.posToday,
};
const NULLS_LAST = ['pos', 'delta', 'ctr', 'impressions', 'clicks'];

function filtered() {
  const q = state.search.trim().toLowerCase();
  let rows = slice.filter(r => {
    if (state.type && r.q['тип'] !== state.type) return false;
    if (state.priority && r.q['приоритет'] !== state.priority) return false;
    if (state.onlyFound && !r.inSerp) return false;
    if (q && !r.q['text'].toLowerCase().includes(q)) return false;
    return true;
  });
  const get = SORT_GET[state.sortKey];
  rows.sort((a, b) => {
    const va = get(a), vb = get(b);
    const na = va == null, nb = vb == null;
    if (NULLS_LAST.includes(state.sortKey) && (na || nb)) {
      if (na && nb) return 0;
      return na ? 1 : -1;
    }
    if (va < vb) return -state.sortDir;
    if (va > vb) return state.sortDir;
    return 0;
  });
  return rows;
}

/* ─── Рендер ────────────────────────────────────────────────────────────── */
function statusChip() {
  const st = $('statusChip');
  if (!DATA) return;
  const gen = DATA.generated ? new Date(DATA.generated) : null;
  const when = gen ? gen.toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '';
  const map = { ok: 'сбор выполнен', 'no-data': 'нет данных — ждём обход', error: 'ошибка сбора' };
  st.className = 'status-chip ' + DATA.status;
  st.textContent = (map[DATA.status] || DATA.status) + (when ? ' · ' + when : '');
}

function renderKpis(rows) {
  const all = slice.length;
  const inSerp = rows.filter(r => r.inSerp).length;
  const withPos = rows.filter(r => r.targetRanks).length;
  const wrong = rows.filter(r => r.wrongPage).length;
  $('kpis').innerHTML = `
    <div class="kpi"><div class="kpi-label">Запросов</div><div class="kpi-value">${all}</div></div>
    <div class="kpi"><div class="kpi-label">В выдаче (${REGION_NAMES[state.region]} · ${DEVICE_NAMES[state.device]})</div><div class="kpi-value accent">${inSerp}</div></div>
    <div class="kpi"><div class="kpi-label">С позицией приёмника</div><div class="kpi-value good">${withPos}</div></div>
    <div class="kpi"><div class="kpi-label">Атакует другая страница</div><div class="kpi-value ${wrong ? 'warn' : ''}">${wrong}</div></div>
    <div class="kpi"><div class="kpi-label">Без данных</div><div class="kpi-value">${all - inSerp}</div></div>`;
}

function posCell(r) {
  const p = r.posToday;
  const cell = `<td class="num clickable"><span class="pos ${p == null ? 'none' : ''}">${p == null ? '—' : p}</span>`;
  if (r.wrongPage) {
    const top = r.otherPages.map(o => bestPos(o.data)).filter(Boolean).sort((a, b) => a - b)[0];
    cell += `<div class="warn-note" title="Приёмник ${r.q['приёмник']} не ранжируется">другая стр. ${top != null ? '· ' + top : ''}</div>`;
  }
  return cell + '</td>';
}
function bestPos(data) {
  const dates = Object.keys(data).sort();
  for (let i = dates.length - 1; i >= 0; i--) {
    if (data[dates[i]].position != null) return data[dates[i]].position;
  }
  return null;
}

function deltaCell(r) {
  const d = r.delta;
  if (d == null) return '<td class="num col-delta"><span class="delta flat">—</span></td>';
  if (d === 0) return '<td class="num col-delta"><span class="delta flat">0</span></td>';
  const better = d < 0; // позиция уменьшилась = улучшение
  return `<td class="num col-delta"><span class="delta ${better ? 'up' : 'down'}">${better ? '▲' : '▼'}${Math.abs(d)}</span></td>`;
}

function sparkSvg(series) {
  if (!series.length) return '<span class="spark empty">нет данных</span>';
  const W = 120, H = 28, PAD = 2;
  const maxPos = Math.max(50, ...series.map(p => p.pos));
  const xs = series.map((_, i) => series.length === 1 ? W / 2 : PAD + i * (W - 2 * PAD) / (series.length - 1));
  const ys = series.map(p => PAD + (p.pos - 1) / (maxPos - 1) * (H - 2 * PAD));
  const pts = xs.map((x, i) => `${x.toFixed(1)},${ys[i].toFixed(1)}`).join(' ');
  const last = pts.split(' ').pop().split(',');
  const color = series[series.length - 1].pos <= 10 ? 'var(--good)' : series[series.length - 1].pos <= 30 ? 'var(--accent)' : 'var(--text-3)';
  return `<svg class="spark" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
    <polyline points="${pts}" fill="none" stroke="${color}" stroke-width="1.6" stroke-linejoin="round"/>
    <circle cx="${last[0]}" cy="${last[1]}" r="2" fill="${color}"/>
  </svg>`;
}

function renderTable() {
  const rows = filtered();
  renderKpis(rows);
  const tb = $('tbody');
  if (!rows.length) {
    tb.innerHTML = '<tr><td colspan="10"><div class="empty-state">Ничего не найдено по фильтрам</div></td></tr>';
    return;
  }
  tb.innerHTML = rows.map((r, i) => {
    const p = r.q['приоритет'];
    return `<tr class="${i % 2 ? 'stripe' : ''}" data-text="${esc(r.q['text'])}">
      <td class="clickable"><span class="q-main">${esc(r.q['text'])}
        <span class="landing">${esc(r.q['приёмник'])}</span></span></td>
      <td><span class="badge ${r.q['тип']}">${esc(r.q['тип'])}</span></td>
      <td><span class="badge ${p}">${esc(p)}</span></td>
      <td class="num col-freq">${fmtNum(r.q['частота'])}</td>
      ${posCell(r)}
      ${deltaCell(r)}
      <td class="num col-imp">${r.imp ? fmtNum(r.imp) : '—'}</td>
      <td class="num col-clicks">${r.clicks ? fmtNum(r.clicks) : '—'}</td>
      <td class="num col-ctr">${fmtCtr(r.ctr)}</td>
      <td>${sparkSvg(r.series)}</td>
    </tr>`;
  }).join('');

  tb.querySelectorAll('tr').forEach(tr => {
    tr.addEventListener('click', () => {
      const text = tr.dataset.text;
      const row = slice.find(r => r.q['text'] === text);
      if (row) openDetail(row);
    });
  });
}

function renderAll() {
  statusChip();
  renderTable();
  const gen = DATA ? DATA.generated : null;
  $('footer').textContent = gen
    ? `Срез: ${REGION_NAMES[state.region]} · ${DEVICE_NAMES[state.device]} · данные Яндекса за 14 дней · обновлено ${new Date(gen).toLocaleString('ru-RU')}`
    : '';
}

/* ─── Деталь запроса ────────────────────────────────────────────────────── */
let detailChart = null;

function openDetail(row) {
  const q = row.q;
  $('dText').textContent = q['text'];
  const meta = [
    `<span class="badge ${q['тип']}">${esc(q['тип'])}</span>`,
    `<span class="badge ${q['приоритет']}">${esc(q['приоритет'])}</span>`,
    q['частота'] ? `частота: <b>${fmtNum(q['частота'])}</b>` : '',
    `приёмник: <b>${esc(q['приёмник'])}</b>`,
    `${REGION_NAMES[state.region]} · ${DEVICE_NAMES[state.device]}`,
  ].filter(Boolean).join(' &nbsp;·&nbsp; ');
  $('dMeta').innerHTML = meta;

  const body = $('dBody');

  // График позиции приёмника
  let chartHtml = '';
  if (row.series.length) {
    chartHtml = `<div class="section-title">Позиция приёмника · 14 дней</div>
      <div class="chart-box"><div id="dChart"></div></div>`;
  }

  // Карта атаки
  const pages = [{ url: row.tKey, data: row.page, isTarget: true }, ...row.otherPages.map(o => ({ url: o.url, data: o.data, isTarget: false }))]
    .filter(p => Object.keys(p.data).length > 0)
    .sort((a, b) => (bestPos(a.data) ?? 999) - (bestPos(b.data) ?? 999));

  const attackHtml = pages.length
    ? `<div class="section-title">Карта атаки — страницы, ранжирующиеся по запросу</div>` +
      pages.map(p => {
        const pos = bestPos(p.data);
        const dates = Object.keys(p.data).sort();
        const sum = s => dates.reduce((acc, d) => acc + (p.data[d][s] || 0), 0);
        const imp = sum('impressions'), clicks = sum('clicks');
        const cls = p.isTarget ? 'is-target' : 'is-wrong';
        const tag = p.isTarget ? '<span class="badge med">приёмник</span>' : '<span class="badge low">другая</span>';
        const dayRows = [...dates].reverse().slice(0, 7).map(d => {
          const s = p.data[d];
          return `<tr><td>${d}</td><td>${s.position ?? '—'}</td><td>${fmtNum(s.impressions)}</td><td>${fmtNum(s.clicks)}</td><td>${fmtCtr(s.ctr)}</td></tr>`;
        }).join('');
        return `<div class="attack-card ${cls}">
          <div class="ac-head">${tag}<span class="ac-url">${esc(p.url)}</span>
            <span class="ac-pos">${pos ? 'позиция ' + pos : 'нет позиции'}</span></div>
          <div class="ac-stats">
            <span>показы: <b>${fmtNum(imp)}</b></span>
            <span>клики: <b>${fmtNum(clicks)}</b></span>
            <span>CTR: <b>${fmtCtr(imp ? clicks / imp * 100 : null)}</b></span>
            <span>дней: <b>${dates.length}</b></span>
          </div>
          <table class="days"><thead><tr><th>Дата</th><th>Позиция</th><th>Показы</th><th>Клики</th><th>CTR</th></tr></thead>
          <tbody>${dayRows || '<tr><td colspan="5">нет данных по дням</td></tr>'}</tbody></table>
        </div>`;
      }).join('')
    : '<div class="empty-state">По запросу нет показов сайта в этом срезе (не в выдаче или не было запросов)</div>';

  body.innerHTML = chartHtml + attackHtml;

  if (row.series.length) {
    renderDetailChart(row.series);
  }

  $('detailBackdrop').hidden = false;
  const d = $('detail');
  d.classList.add('open');
  d.setAttribute('aria-hidden', 'false');
}

function renderDetailChart(series) {
  if (detailChart) { detailChart.destroy(); detailChart = null; }
  const xs = series.map(p => new Date(p.date + 'T12:00:00').getTime());
  const ys = series.map(p => p.pos);
  const maxPos = Math.max(50, ...ys);
  detailChart = new uPlot({
    width: 660, height: 240,
    legend: { show: true },
    scales: { y: { range: () => [maxPos, 1] } },
    axes: [
      { stroke: 'var(--text-3)', grid: { stroke: 'var(--border)' } },
      {
        stroke: 'var(--text-3)', grid: { stroke: 'var(--border)' },
        values: (u, vals) => vals.map(v => v + ''),
        size: 40,
      },
    ],
    series: [
      { label: 'дата' },
      { label: 'позиция', stroke: 'var(--accent)', width: 2,
        points: { size: 5, stroke: 'var(--accent)' },
        value: (u, v) => v == null ? '—' : v + '' },
    ],
  }, [[...xs], [...ys]], document.getElementById('dChart'));
}

function closeDetail() {
  const d = $('detail');
  d.classList.remove('open');
  d.setAttribute('aria-hidden', 'true');
  $('detailBackdrop').hidden = true;
  if (detailChart) { detailChart.destroy(); detailChart = null; }
}

/* ─── События ───────────────────────────────────────────────────────────── */
$('regionSeg').addEventListener('click', e => {
  const b = e.target.closest('button');
  if (!b) return;
  state.region = b.dataset.region;
  document.querySelectorAll('#regionSeg button').forEach(x => x.classList.toggle('active', x === b));
  buildSlice();
});
$('deviceSeg').addEventListener('click', e => {
  const b = e.target.closest('button');
  if (!b) return;
  state.device = b.dataset.device;
  document.querySelectorAll('#deviceSeg button').forEach(x => x.classList.toggle('active', x === b));
  buildSlice();
});
$('search').addEventListener('input', e => { state.search = e.target.value; renderTable(); });
$('typeFilter').addEventListener('change', e => { state.type = e.target.value; renderTable(); });
$('priorityFilter').addEventListener('change', e => { state.priority = e.target.value; renderTable(); });
$('onlyFound').addEventListener('change', e => { state.onlyFound = e.target.checked; renderTable(); });
$('reload').addEventListener('click', load);

document.querySelectorAll('#queriesTable th[data-sort]').forEach(th => {
  th.addEventListener('click', () => {
    const key = th.dataset.sort;
    if (state.sortKey === key) state.sortDir = -state.sortDir;
    else { state.sortKey = key; state.sortDir = 1; }
    document.querySelectorAll('#queriesTable th').forEach(x => {
      x.classList.toggle('sorted', x === th);
      const a = x.querySelector('.arrow');
      if (a) a.remove();
    });
    th.classList.add('sorted');
    const span = document.createElement('span');
    span.className = 'arrow';
    span.textContent = state.sortDir === 1 ? '▲' : '▼';
    th.appendChild(span);
    renderTable();
  });
});

$('dClose').addEventListener('click', closeDetail);
$('detailBackdrop').addEventListener('click', closeDetail);
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDetail(); });

/* ─── Темы / шрифт / масштаб ────────────────────────────────────────────── */
function setPref(key, attr, value, selectId) {
  localStorage.setItem(key, value);
  document.documentElement.setAttribute(attr, value);
  $(selectId).value = value;
}
$('themeSelect').addEventListener('change', e => setPref('wm-theme', 'data-theme', e.target.value, 'themeSelect'));
$('fontSelect').addEventListener('change', e => setPref('wm-font', 'data-font', e.target.value, 'fontSelect'));
$('scaleSelect').addEventListener('change', e => setPref('wm-scale', 'data-scale', e.target.value, 'scaleSelect'));
['themeSelect', 'fontSelect', 'scaleSelect'].forEach(id => {
  const v = localStorage.getItem({ themeSelect: 'wm-theme', fontSelect: 'wm-font', scaleSelect: 'wm-scale' }[id]);
  if (v) $(id).value = v;
});

/* ─── Сбор позиций ──────────────────────────────────────────────────────── */
let collectTimer = null;
async function collectNow() {
  const btn = $('collectBtn');
  btn.disabled = true;
  btn.textContent = 'сбор идёт…';
  try {
    await fetch('/api/collect', { method: 'POST' });
    collectTimer = setInterval(async () => {
      try {
        const st = await (await fetch('/api/status', { cache: 'no-store' })).json();
        if (!st.running) {
          clearInterval(collectTimer);
          collectTimer = null;
          btn.disabled = false;
          btn.textContent = '⟳ Собрать сейчас';
          await load();
        }
      } catch (e) { /* сервер ещё жив — ждём */ }
    }, 5000);
  } catch (e) {
    btn.disabled = false;
    btn.textContent = '⟳ Собрать сейчас';
    alert('Не удалось запустить сбор: сервер не отвечает на /api/collect');
  }
}
$('collectBtn').addEventListener('click', collectNow);

load();
