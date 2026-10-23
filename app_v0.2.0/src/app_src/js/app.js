/* 職災小卡 手機版：畫面流程沿用 v0.1 電腦版，只把出圖改成在瀏覽器裡做。 */
(function () {
'use strict';
const APP_VERSION = '0.2.0';
const BUILD = '__BUILD__';
// 壞檔在清單上的標示（驗收第 10 條的用字）；要換字只改這裡
const BROKEN_LABEL = '這個案例讀不出來';
const DISCLAIMER = '案例內容由 AI 整理，正式使用前請自己對照判決核對。';
const TEMPLATES = [['classic', '新第一版'], ['light', '淺色資訊圖'], ['standard', '原版']];
const SKIN_FILES = ['original', 'style1', 'style1_print', 'style2', 'style3', 'style4', 'style5', 'style6', 'style7'];
const MSG = {
  start: '請先在上面選案例，再按「產生小卡」。',
  loaded: '案例清單已讀取。',
  none: 'cases 資料夾裡沒有可以用的案例。',
  pick: '請先選一個案例。',
  busy: '產生中，請稍候……',
  badFile: BROKEN_LABEL + '，請換一個案例或檢查檔案內容。',
  cannot: '這個案例產生不出小卡，請檢查案例內容是否完整（法院、案號、判決日期、圖卡內容）。',
  badTpl: '版型不正確，請重新選擇。',
  badSkin: '風格不正確，請重新選擇。',
  oops: '發生問題，請再試一次。',
  listFail: '案例清單讀不出來，請按「重新讀取」再試一次。',
};
const $ = id => document.getElementById(id);
const BASE = new URL('./', location.href).href;   // 相對路徑：放在 GitHub Pages 子目錄也能用
let SKINS = {}, CASES = [], current = null;       // current = {blob, url, name}

async function getJSON(path) {
  const r = await fetch(BASE + path, { cache: 'no-cache' });
  if (!r.ok) throw new Error(r.status);
  return r.json();
}
async function getText(path) {
  const r = await fetch(BASE + path);
  if (!r.ok) throw new Error(r.status);
  return r.text();
}
function okCase(d) { return d && typeof d === 'object' && !Array.isArray(d) && d.card && typeof d.card === 'object' && !Array.isArray(d.card) && d.source && typeof d.source === 'object' && !Array.isArray(d.source); }
function stem(f) { return f.replace(/\.json$/i, ''); }

async function loadSkins() {
  const list = await Promise.all(SKIN_FILES.map(id => getJSON('skins/skin_' + id + '.json')));
  SKINS = {}; list.forEach(s => { SKINS[s.id] = s; });
  const ids = Object.keys(SKINS).sort((a, b) => (a !== 'original') - (b !== 'original') || (a < b ? -1 : a > b ? 1 : 0));
  return ids.map(id => ({ id, name: SKINS[id].name || id }));
}
async function loadCases() {
  const idx = await getJSON('cases/index.json');
  const files = (idx && Array.isArray(idx.cases)) ? idx.cases.filter(f => typeof f === 'string') : [];
  return Promise.all(files.slice().sort().map(async file => {
    try {
      const data = await getJSON('cases/' + encodeURIComponent(file));
      if (!okCase(data)) throw new Error('bad');
      return { file, title: data.title || stem(file), ok: true, data };
    } catch (e) { return { file, title: file, ok: false, note: BROKEN_LABEL }; }
  }));
}
async function load() {
  const keep = (document.querySelector('input[name=c]:checked') || {}).value;
  $('cases').innerHTML = '';
  try {
    if (!$('tpl').options.length) {
      TEMPLATES.forEach(([id, n]) => $('tpl').add(new Option(n, id)));
      (await loadSkins()).forEach(s => $('skin').add(new Option(s.name, s.id)));
    }
    CASES = await loadCases();
  } catch (e) { $('msg').textContent = MSG.listFail; return; }
  CASES.forEach(c => {
    const l = document.createElement('label'); l.className = 'case' + (c.ok ? '' : ' bad');
    if (c.ok) { const r = document.createElement('input'); r.type = 'radio'; r.name = 'c'; r.value = c.file; l.append(r); }
    l.append(c.ok ? c.title : `${c.file}（${c.note}）`);
    $('cases').append(l);
  });
  const r = [...document.querySelectorAll('input[name=c]')];
  (r.find(x => x.value === keep) || r[0] || {}).checked = true;
  $('disc').textContent = DISCLAIMER; tplChange();
  $('msg').textContent = r.length ? MSG.loaded : MSG.none;
}
function tplChange() {
  const c = $('tpl').value === 'classic'; $('skin').disabled = !c;
  if (!c) $('skin').value = 'original';
  $('skinnote').textContent = c ? '' : '只有新第一版可以換風格';
}
function clearResult() {
  $('result').innerHTML = ''; $('picwrap').hidden = true;
  if (current) { URL.revokeObjectURL(current.url); current = null; }
  $('pic').removeAttribute('src');
}
function esc(s) { return String(s).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch])); }

async function generate() {
  const sel = document.querySelector('input[name=c]:checked');
  if (!sel) { $('msg').textContent = MSG.pick; return; }
  const template = $('tpl').value; let skin = $('skin').value; const draft = $('draft').checked;
  if (!TEMPLATES.some(t => t[0] === template)) { $('msg').textContent = MSG.badTpl; return; }
  if (template !== 'classic') skin = 'original';
  if (!SKINS[skin]) { $('msg').textContent = MSG.badSkin; return; }
  const c = CASES.find(x => x.file === sel.value);
  if (!c || !c.ok) { $('msg').textContent = MSG.badFile; return; }
  $('msg').textContent = MSG.busy; clearResult(); $('go').disabled = true;
  try {
    let res;
    try {
      const hero = (c.data.card && c.data.card.hero) || {};
      const assets = { standardCss: await getText('design/standard.css') };
      // 原版右上用照片（發包人 2026-10-23 同意沿用）；案例沒有照片時改用示意圖 SVG
      if (template === 'standard') assets.heroPhotoUrl = BASE + 'hero_library/' + (hero.photo || hero.file);
      else assets.heroSvg = await getText('hero_library/' + hero.file);
      res = await CardRender.renderCard({ kase: c.data, template, skin, draft, skinsById: SKINS, assets, base: BASE, host: $('stage') });
    } catch (e) { console.error(e); $('msg').textContent = MSG.cannot; return; }
    $('msg').textContent = '';
    const failed = res.checks.filter(x => !x[1]);
    const problems = CardRender.friendly(res.checks, res.missing);
    if (failed.length) {
      $('result').innerHTML = `<div class="warn"><b>檢查沒過（${failed.length} 項），請修改案例內容：</b><ul>${problems.map(f => '<li>' + esc(f) + '</li>').join('')}</ul>` +
        (res.blob ? '下面的圖照原樣產生，讓你看哪裡超出；文字沒有被縮小或刪減。' : '') +
        `<details class="diag"><summary>給維護人員看的詳細資料</summary><pre>${esc([navigator.userAgent, ...(res.diag || []), ...failed.map(x => x[0] + '：' + JSON.stringify(x[2]))].join('\n'))}</pre></details></div>`;
    } else {
      $('result').innerHTML = `<div class="okmsg">檢查全部通過（${res.checks.length} 項）</div>`;
    }
    if (res.blob) {
      const name = `${stem(c.file)}_${template}_${skin}${draft ? '_草稿' : ''}.png`;
      current = { blob: res.blob, url: URL.createObjectURL(res.blob), name, sha256: res.sha256 };
      $('pic').src = current.url; $('picwrap').hidden = false;
    }
    window.__lastResult = { checks: res.checks, rects: res.measure ? res.measure.textRects : null, sha256: res.sha256, name: current && current.name };
  } catch (e) { console.error(e); $('msg').textContent = MSG.oops; }
  finally { $('go').disabled = false; }
}
function showFull() {
  $('fullpic').src = current.url; $('full').hidden = false;
}
async function save() {
  if (!current) return;
  // 存的就是畫面上這一份 PNG（不重畫）
  const file = new File([current.blob], current.name, { type: 'image/png' });
  if (navigator.canShare && navigator.share && navigator.canShare({ files: [file] })) {
    try { await navigator.share({ files: [file] }); return; }
    catch (e) { if (e && e.name === 'AbortError') return; }
  }
  showFull();
}
$('tpl').onchange = tplChange; $('reload').onclick = load; $('go').onclick = generate; $('save').onclick = save;
$('closefull').onclick = () => { $('full').hidden = true; };
$('ver').textContent = `版本 ${APP_VERSION}（${BUILD}）`;

if ('serviceWorker' in navigator && location.protocol !== 'file:') {
  let reloaded = false;
  const hadController = !!navigator.serviceWorker.controller;
  navigator.serviceWorker.addEventListener('controllerchange', () => { if (hadController && !reloaded) { reloaded = true; location.reload(); } });
  navigator.serviceWorker.register('sw.js').then(reg => reg.update()).catch(() => {});
}
window.__app = { BROKEN_LABEL, APP_VERSION, BUILD, get current() { return current; } };
CardRender.init(BASE).then(load).catch(() => { $('msg').textContent = MSG.listFail; });
})();
